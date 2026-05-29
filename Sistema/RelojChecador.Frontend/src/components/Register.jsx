import "./login.css";
import { useEffect, useState } from "react";

function buildDefaultModelLabel(nombres, apellidoPaterno) {
  const base = `${nombres} ${apellidoPaterno}`
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9]+/g, "")
    .trim();

  return base ? `${base}Set` : "";
}

function Register({ volver, abrirCamara }) {
  const [numeroEmpleado, setNumeroEmpleado] = useState("");
  const [apellidoPaterno, setApellidoPaterno] = useState("");
  const [apellidoMaterno, setApellidoMaterno] = useState("");
  const [nombres, setNombres] = useState("");
  const [nombreEtiquetaModelo, setNombreEtiquetaModelo] = useState("");
  const [correo, setCorreo] = useState("");
  const [rol, setRol] = useState("Usuario");
  const [mensaje, setMensaje] = useState(
    "Llena los datos. El usuario solo se guardará si el modelo se entrena correctamente."
  );
  const [mostrarMensaje, setMostrarMensaje] = useState(true);

  const nombreCompleto = `${nombres} ${apellidoPaterno} ${apellidoMaterno}`
    .replace(/\s+/g, " ")
    .trim();

  const etiquetaFinal = nombreEtiquetaModelo.trim() || buildDefaultModelLabel(nombres, apellidoPaterno);

  const formValido =
    numeroEmpleado.trim() !== "" &&
    apellidoPaterno.trim() !== "" &&
    apellidoMaterno.trim() !== "" &&
    nombres.trim() !== "" &&
    etiquetaFinal.trim() !== "" &&
    rol.trim() !== "";

  useEffect(() => {
    const timer = setTimeout(() => {
      setMostrarMensaje(false);
    }, 7000);

    return () => clearTimeout(timer);
  }, []);

  const continuarCaptura = () => {
    if (!formValido) return;

    const payload = {
      numero_empleado: numeroEmpleado.trim(),
      nombre: nombreCompleto,
      nombre_etiqueta_modelo: etiquetaFinal.trim(),
      correo: correo.trim() || null,
      rol,
      activo: true,
    };

    setMensaje("Abriendo cámara. Capturaremos 320 imágenes antes de entrenar.");
    setMostrarMensaje(true);
    abrirCamara(payload);
  };

  return (
    <div className="container">
      {mostrarMensaje && <div className="toast-mensaje">{mensaje}</div>}

      <div className="card register-card">
        <button
          className="icon"
          onClick={continuarCaptura}
          disabled={!formValido}
          style={{
            opacity: formValido ? 1 : 0.3,
            cursor: formValido ? "pointer" : "not-allowed",
          }}
          title="Capturar rostros y entrenar modelo"
        >
          👤
        </button>

        <h2>Registrar usuario</h2>
        <h5>
          Primero se capturan 320 imágenes del rostro. El backend usará 220 para Train y
          100 para Validation. Si el entrenamiento falla, el usuario no se guarda.
        </h5>

        <input
          placeholder="Número de empleado"
          value={numeroEmpleado}
          onChange={(e) => setNumeroEmpleado(e.target.value)}
        />

        <input
          placeholder="Apellido Paterno"
          value={apellidoPaterno}
          onChange={(e) => setApellidoPaterno(e.target.value)}
        />

        <input
          placeholder="Apellido Materno"
          value={apellidoMaterno}
          onChange={(e) => setApellidoMaterno(e.target.value)}
        />

        <input
          placeholder="Nombre(s)"
          value={nombres}
          onChange={(e) => setNombres(e.target.value)}
        />

        <input
          placeholder={`Etiqueta del modelo, ejemplo: ${buildDefaultModelLabel(nombres, apellidoPaterno) || "SantosSet"}`}
          value={nombreEtiquetaModelo}
          onChange={(e) => setNombreEtiquetaModelo(e.target.value)}
        />

        <input
          placeholder="Correo electrónico opcional"
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
        />

        <select className="input" value={rol} onChange={(e) => setRol(e.target.value)}>
          <option value="Usuario">Usuario</option>
          <option value="Ejecutivo">Ejecutivo</option>
          <option value="Seguridad">Seguridad</option>
          <option value="Limpieza">Limpieza</option>
          <option value="Guardia">Guardia</option>
          <option value="Administrador">Administrador</option>
        </select>

        <button className="btn-login" onClick={continuarCaptura} disabled={!formValido}>
          Continuar a captura y entrenamiento
        </button>

        <button className="btn-register" onClick={volver}>
          Volver
        </button>
      </div>
    </div>
  );
}

export default Register;
