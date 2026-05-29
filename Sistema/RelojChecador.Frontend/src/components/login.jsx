import "./login.css";

function Login({ irCamara, irRegistro }) {
  return (
    <div className="container">
      <div className="card">
        <div className="icon">📷</div>

        <h2>Reconocimiento Facial</h2>

        <button className="btn-login" onClick={irCamara}>
          Iniciar
        </button>

        <button className="btn-register" onClick={irRegistro}>
          Registrar usuario
        </button>
      </div>
    </div>
  );
}

export default Login;
