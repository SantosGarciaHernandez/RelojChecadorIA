import { useState } from "react";

import Login from "./components/login";
import Camera from "./components/camera";
import Register from "./components/Register";
import Camera_Register from "./components/camera_register";

function App() {
  const [pantalla, setPantalla] = useState("login");
  const [usuarioRegistrado, setUsuarioRegistrado] = useState(null);

  return (
    <>
      {pantalla === "login" && (
        <Login
          irCamara={() => setPantalla("camera")}
          irRegistro={() => setPantalla("register")}
        />
      )}

      {pantalla === "camera" && <Camera volver={() => setPantalla("login")} />}

      {pantalla === "camera_register" && (
        <Camera_Register
          usuario={usuarioRegistrado}
          volver={() => {
            setUsuarioRegistrado(null);
            setPantalla("login");
          }}
        />
      )}

      {pantalla === "register" && (
        <Register
          volver={() => setPantalla("login")}
          abrirCamara={(usuario) => {
            setUsuarioRegistrado(usuario);
            setPantalla("camera_register");
          }}
        />
      )}
    </>
  );
}

export default App;
