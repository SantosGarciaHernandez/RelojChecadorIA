import { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import * as faceapi from "face-api.js";
import "./camesa.css";
import { getTrainingWsUrl, registerUserWithTraining } from "../services/api";
import { cropFaceToDataUrl, drawExpandedFaceBox } from "../utils/faceCrop";

const TOTAL_CAPTURAS = 400;
const TRAIN_CAPTURAS = 300;
const VALIDATION_CAPTURAS = 100;
const CAPTURE_INTERVAL_MS = 300;

function buildJobId() {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID();
  return `training-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function Camera_Register({ volver, usuario }) {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);
  const wsRef = useRef(null);
  const imagenesRef = useRef([]);
  const ultimoCaptureRef = useRef(0);
  const entrenamientoIniciadoRef = useRef(false);
  const capturaCanceladaRef = useRef(false);
  const jobIdRef = useRef(buildJobId());

  const [mensaje, setMensaje] = useState("Cargando detector facial...");
  const [capturas, setCapturas] = useState(0);
  const [fase, setFase] = useState("loading");
  const [trainingProgress, setTrainingProgress] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);

  const porcentajeCaptura = Math.min(100, Math.round((capturas / TOTAL_CAPTURAS) * 100));
  const puedeSalir = fase === "completed" || fase === "failed" || fase === "cancelled";
  const puedeCancelarCaptura = fase === "loading" || fase === "capturing";

  const cerrarWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const conectarWebSocketEntrenamiento = () => {
    cerrarWebSocket();

    const socket = new WebSocket(getTrainingWsUrl(jobIdRef.current));
    wsRef.current = socket;

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setTrainingProgress(data);
        if (data.message) setMensaje(data.message);
        if (data.status === "completed") setFase("completed");
        if (data.status === "failed") {
          setFase("failed");
          setError(data.message || "Falló el entrenamiento del modelo.");
        }
      } catch (parseError) {
        console.error("No se pudo leer progreso de entrenamiento:", parseError);
      }
    };

    socket.onerror = (event) => {
      console.error("Error WebSocket entrenamiento:", event);
    };
  };

  const limpiarIntervalo = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const iniciarEntrenamiento = async () => {
    if (entrenamientoIniciadoRef.current) return;
    entrenamientoIniciadoRef.current = true;
    limpiarIntervalo();

    capturaCanceladaRef.current = false;
    setFase("training");
    setMensaje("Captura terminada. Enviando imágenes al backend...");
    conectarWebSocketEntrenamiento();

    try {
      const payload = {
        ...usuario,
        job_id: jobIdRef.current,
        images_base64: imagenesRef.current,
      };

      const data = await registerUserWithTraining(payload);
      setResultado(data);
      setFase("completed");
      setMensaje("Entrenamiento terminado y usuario guardado correctamente.");
    } catch (apiError) {
      console.error("Error entrenando usuario:", apiError);
      setError(apiError.message);
      setFase("failed");
      setMensaje(`Error: ${apiError.message}`);
    }
  };

  const cancelarCaptura = () => {
    if (fase === "training" || fase === "completed") return;

    limpiarIntervalo();
    cerrarWebSocket();
    imagenesRef.current = [];
    ultimoCaptureRef.current = 0;
    entrenamientoIniciadoRef.current = false;
    capturaCanceladaRef.current = true;

    setCapturas(0);
    setTrainingProgress(null);
    setResultado(null);
    setError(null);
    setFase("cancelled");
    setMensaje("Captura cancelada. No se enviaron imágenes al backend y el usuario no fue guardado.");
  };

  const iniciarCaptura = () => {
    limpiarIntervalo();
    capturaCanceladaRef.current = false;
    setFase("capturing");
    setMensaje("Detector cargado. Mantén el rostro dentro del cuadro hasta capturar 320 imágenes.");

    intervalRef.current = setInterval(async () => {
      if (capturaCanceladaRef.current) return;

      try {
        const video = webcamRef.current?.video;
        if (!video || video.videoWidth === 0 || video.videoHeight === 0) return;

        const detections = await faceapi.detectAllFaces(
          video,
          new faceapi.TinyFaceDetectorOptions({ inputSize: 224, scoreThreshold: 0.5 })
        );

        if (capturaCanceladaRef.current) return;

        const canvas = canvasRef.current;
        if (!canvas) return;

        const displaySize = {
          width: video.videoWidth,
          height: video.videoHeight,
        };

        faceapi.matchDimensions(canvas, displaySize);
        const resized = faceapi.resizeResults(detections, displaySize);
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (detections.length === 0) {
          setMensaje(`Sin rostro detectado. Capturas: ${imagenesRef.current.length}/${TOTAL_CAPTURAS}`);
          return;
        }

        const rostroOriginal = detections.reduce((mayor, actual) => {
          const mayorArea = mayor.box.width * mayor.box.height;
          const actualArea = actual.box.width * actual.box.height;
          return actualArea > mayorArea ? actual : mayor;
        }, detections[0]);

        const rostroDibujado = resized.reduce((mayor, actual) => {
          const mayorArea = mayor.box.width * mayor.box.height;
          const actualArea = actual.box.width * actual.box.height;
          return actualArea > mayorArea ? actual : mayor;
        }, resized[0]);

        drawExpandedFaceBox(ctx, rostroDibujado, displaySize.width, displaySize.height);

        const ahora = Date.now();
        if (ahora - ultimoCaptureRef.current < CAPTURE_INTERVAL_MS) return;
        ultimoCaptureRef.current = ahora;

        if (imagenesRef.current.length >= TOTAL_CAPTURAS) return;

        const faceBase64 = cropFaceToDataUrl(video, rostroOriginal, {
          outputWidth: 128,
          outputHeight: 128,
          quality: 0.86,
        });

        if (capturaCanceladaRef.current) return;

        imagenesRef.current.push(faceBase64);
        const total = imagenesRef.current.length;
        setCapturas(total);
        setMensaje(`Capturando rostro: ${total}/${TOTAL_CAPTURAS}`);

        if (total >= TOTAL_CAPTURAS && !capturaCanceladaRef.current) {
          await iniciarEntrenamiento();
        }
      } catch (detectError) {
        console.error("Error capturando rostro:", detectError);
        setMensaje(`Error capturando rostro: ${detectError.message}`);
      }
    }, 180);
  };

  useEffect(() => {
    document.body.classList.add("camera-screen-active");

    const load = async () => {
      try {
        await faceapi.nets.tinyFaceDetector.loadFromUri("/models");
        if (capturaCanceladaRef.current) return;
        iniciarCaptura();
      } catch (loadError) {
        console.error("Error cargando detector:", loadError);
        setError(loadError.message);
        setFase("failed");
        setMensaje(`Error cargando detector facial: ${loadError.message}`);
      }
    };

    load();

    return () => {
      document.body.classList.remove("camera-screen-active");
      limpiarIntervalo();
      cerrarWebSocket();
    };
  }, []);

  return (
    <div className="camera-container training-camera-container">
      <div className="notificacion">{mensaje}</div>

      <main className="camera-layout training-layout">
        <section className="scan-panel">
          <div className="scan-header">
            <h1>Entrenamiento facial</h1>
            <p className="camera-status">
              Usuario: <strong>{usuario?.nombre}</strong> · Etiqueta: {" "}
              <strong>{usuario?.nombre_etiqueta_modelo}</strong>
            </p>
          </div>

          <div className="camera-box">
            <Webcam
              ref={webcamRef}
              className="webcam"
              muted
              audio={false}
              screenshotFormat="image/jpeg"
              videoConstraints={{
                facingMode: "user",
                width: { ideal: 960 },
                height: { ideal: 540 },
              }}
            />

            <canvas ref={canvasRef} className="face-canvas" />
          </div>

          <div className="camera-actions">
            {puedeCancelarCaptura && (
              <button className="btn-cancel-capture" onClick={cancelarCaptura}>
                Cancelar captura
              </button>
            )}

            {fase === "training" && (
              <button className="btn-register" disabled>
                Entrenamiento en proceso
              </button>
            )}

            {puedeSalir && (
              <button className="btn-register" onClick={volver}>
                {fase === "cancelled" ? "Volver al formulario" : "Finalizar"}
              </button>
            )}
          </div>
        </section>

        <aside className="side-panel training-side-panel">
          <section className="api-result training-card">
            <strong>Captura de imágenes</strong>
            <span>{capturas}/{TOTAL_CAPTURAS} imágenes capturadas</span>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${porcentajeCaptura}%` }} />
            </div>
            <span>Train: {Math.min(capturas, TRAIN_CAPTURAS)}/{TRAIN_CAPTURAS}</span>
            <span>
              Validation: {Math.max(0, capturas - TRAIN_CAPTURAS)}/{VALIDATION_CAPTURAS}
            </span>
          </section>

          <section className="api-result training-card">
            <strong>Entrenamiento del modelo</strong>
            <span>Estado: {trainingProgress?.status || fase}</span>
            <span>{trainingProgress?.message || "Esperando terminar captura..."}</span>
            <div className="progress-track">
              <div
                className="progress-fill training-progress-fill"
                style={{ width: `${trainingProgress?.percent || 0}%` }}
              />
            </div>
            <span>Avance backend: {trainingProgress?.percent || 0}%</span>
            {trainingProgress?.extra?.epoch && (
              <span>
                Época {trainingProgress.extra.epoch}/{trainingProgress.extra.epochs} · Acc: {" "}
                {(trainingProgress.extra.accuracy * 100).toFixed(1)}% · Val: {" "}
                {(trainingProgress.extra.val_accuracy * 100).toFixed(1)}%
              </span>
            )}
          </section>

          {resultado && (
            <section className="api-result training-card success-card">
              <strong>Registro completado</strong>
              <span>{resultado.message}</span>
              <span>Usuario: {resultado.user?.nombre}</span>
              <span>Empleado: {resultado.user?.numero_empleado}</span>
            </section>
          )}

          {error && (
            <section className="api-result training-card error-card">
              <strong>Error</strong>
              <span>{error}</span>
              <span>El usuario no fue guardado porque el entrenamiento no terminó correctamente.</span>
            </section>
          )}

          {fase === "cancelled" && (
            <section className="api-result training-card warning-card">
              <strong>Captura cancelada</strong>
              <span>Se descartaron las imágenes capturadas.</span>
              <span>No se entrenó el modelo y no se guardó el usuario.</span>
            </section>
          )}
        </aside>
      </main>
    </div>
  );
}

export default Camera_Register;
