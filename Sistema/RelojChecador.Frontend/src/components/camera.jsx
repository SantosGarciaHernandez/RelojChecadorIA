import { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import * as faceapi from "face-api.js";
import "./camesa.css";
import RecentAttendanceTable from "./RecentAttendanceTable";
import { getEntryPcName, getExitPcName, getPcNameByMode, predictFaceCrop } from "../services/api";
import { cropFaceToDataUrl, drawExpandedFaceBox } from "../utils/faceCrop";

function Camera({ volver }) {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);
  const procesandoRef = useRef(false);
  const ultimaPeticionRef = useRef(0);
  const ultimaVozRef = useRef("");
  const modoRegistroRef = useRef("Entrada");

  const [estado, setEstado] = useState("Cargando detector facial...");
  const [ultimaRespuesta, setUltimaRespuesta] = useState(null);
  const [modoRegistro, setModoRegistro] = useState("Entrada");

  const hablar = (texto) => {
    const synth = window.speechSynthesis;

    if (!synth || !texto) return;

    const ahora = Date.now();
    const mismaFrase = ultimaVozRef.current === texto;

    if (mismaFrase && ahora - ultimaPeticionRef.current < 5000) return;

    ultimaVozRef.current = texto;

    const utterance = new SpeechSynthesisUtterance(texto);
    utterance.lang = "es-MX";
    utterance.rate = 1;

    synth.cancel();
    synth.speak(utterance);
  };

  const construirMensaje = (data) => {
    if (data.recognized) {
      const tipo = data.record_type ? ` ${data.record_type}` : " registro";
      const confianza = data.confidence != null ? `, confianza ${(data.confidence * 100).toFixed(1)} por ciento` : "";
      return `${tipo} autorizado para ${data.name}${confianza}`;
    }

    return data.message || "Usuario no autorizado, posible intruso";
  };

  const consultarPrediccion = async (video, detection) => {
    if (procesandoRef.current) return;

    const ahora = Date.now();
    const intervaloMinimoMs = 2500;

    if (ahora - ultimaPeticionRef.current < intervaloMinimoMs) return;

    procesandoRef.current = true;
    ultimaPeticionRef.current = ahora;

    try {
      setEstado("Rostro detectado. Consultando API...");

      const faceBase64 = cropFaceToDataUrl(video, detection);
      const pcName = getPcNameByMode(modoRegistroRef.current);
      const data = await predictFaceCrop(faceBase64, pcName);

      console.log("Respuesta API detección:", data);
      setUltimaRespuesta(data);

      const mensaje = construirMensaje(data);
      setEstado(mensaje);
      hablar(mensaje);
    } catch (error) {
      console.error("Error consultando API:", error);
      const mensaje = `Error en la verificación: ${error.message}`;
      setEstado(mensaje);
      hablar("Error en la verificación del usuario");
    } finally {
      procesandoRef.current = false;
    }
  };

  const cambiarModoRegistro = (nuevoModo) => {
    modoRegistroRef.current = nuevoModo;
    setModoRegistro(nuevoModo);
    setEstado(`Modo ${nuevoModo} seleccionado. Posiciona tu rostro frente a la cámara.`);
  };

  const iniciarDeteccion = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);

    intervalRef.current = setInterval(async () => {
      try {
        const video = webcamRef.current?.video;

        if (!video || video.videoWidth === 0 || video.videoHeight === 0) return;

        const detections = await faceapi.detectAllFaces(
          video,
          new faceapi.TinyFaceDetectorOptions({ inputSize: 224, scoreThreshold: 0.5 })
        );

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
          setEstado("Sin rostro detectado");
          return;
        }

        const rostroMasGrande = detections.reduce((mayor, actual) => {
          const mayorArea = mayor.box.width * mayor.box.height;
          const actualArea = actual.box.width * actual.box.height;
          return actualArea > mayorArea ? actual : mayor;
        }, detections[0]);

        const rostroMasGrandeRedimensionado = resized.reduce((mayor, actual) => {
          const mayorArea = mayor.box.width * mayor.box.height;
          const actualArea = actual.box.width * actual.box.height;
          return actualArea > mayorArea ? actual : mayor;
        }, resized[0]);

        drawExpandedFaceBox(ctx, rostroMasGrandeRedimensionado, displaySize.width, displaySize.height);

        await consultarPrediccion(video, rostroMasGrande);
      } catch (error) {
        console.error("Error en detección:", error);
        setEstado(`Error en detección: ${error.message}`);
      }
    }, 700);
  };

  useEffect(() => {
    document.body.classList.add("camera-screen-active");

    const load = async () => {
      try {
        await faceapi.nets.tinyFaceDetector.loadFromUri("/models");
        setEstado("Detector cargado. Posiciona tu rostro frente a la cámara.");
        iniciarDeteccion();
      } catch (error) {
        console.error("Error cargando modelos de face-api:", error);
        setEstado(`Error cargando detector facial: ${error.message}`);
      }
    };

    load();

    return () => {
      document.body.classList.remove("camera-screen-active");
      if (intervalRef.current) clearInterval(intervalRef.current);
      window.speechSynthesis?.cancel();
    };
  }, []);

  return (
    <div className="camera-container">
      <div className="notificacion">{estado}</div>

      <main className="camera-layout">
        <section className="scan-panel">
          <div className="scan-header">
            <h1>Escaneo Facial</h1>
            <p className="camera-status">
              Modo actual: <strong>{modoRegistro}</strong> · Equipo simulado:{" "}
              <strong>{getPcNameByMode(modoRegistro)}</strong>
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
            <div className="mode-toggle" aria-label="Seleccionar modo de registro">
              <button
                type="button"
                className={modoRegistro === "Entrada" ? "active" : ""}
                onClick={() => cambiarModoRegistro("Entrada")}
                title={`Usar ${getEntryPcName()}`}
              >
                Entrada
              </button>
              <button
                type="button"
                className={modoRegistro === "Salida" ? "active" : ""}
                onClick={() => cambiarModoRegistro("Salida")}
                title={`Usar ${getExitPcName()}`}
              >
                Salida
              </button>
            </div>

            <button className="btn-register" onClick={volver}>
              Salir
            </button>
          </div>
        </section>

        <aside className="side-panel">
          <section className="api-result">
            <strong>Última respuesta</strong>
            {ultimaRespuesta ? (
              <>
                <span>{ultimaRespuesta.message}</span>
                {ultimaRespuesta.name && <span>Usuario: {ultimaRespuesta.name}</span>}
                {ultimaRespuesta.record_type && <span>Tipo: {ultimaRespuesta.record_type}</span>}
                {ultimaRespuesta.confidence != null && (
                  <span>Confianza: {(ultimaRespuesta.confidence * 100).toFixed(2)}%</span>
                )}
              </>
            ) : (
              <span>Esperando primera detección...</span>
            )}
          </section>

          <RecentAttendanceTable />
        </aside>
      </main>
    </div>
  );
}

export default Camera;
