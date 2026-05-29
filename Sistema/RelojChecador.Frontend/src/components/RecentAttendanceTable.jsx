import { useEffect, useMemo, useRef, useState } from "react";
import { getRecentAttendance, getRecentAttendanceWsUrl } from "../services/api";

function formatTime(value) {
  if (!value) return "--:--";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--:--";

  return date.toLocaleTimeString("es-MX", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatConfidence(value) {
  if (value == null) return "--";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function RecentAttendanceTable() {
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const [records, setRecords] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("Conectando...");

  const sortedRecords = useMemo(() => records.slice(0, 10), [records]);

  useEffect(() => {
    let cancelled = false;

    const loadInitialData = async () => {
      try {
        const data = await getRecentAttendance(10);
        if (!cancelled) setRecords(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Error cargando registros iniciales:", error);
      }
    };

    const connectSocket = () => {
      if (cancelled) return;

      const socket = new WebSocket(getRecentAttendanceWsUrl());
      socketRef.current = socket;
      setConnectionStatus("Conectando...");

      socket.onopen = () => {
        setConnectionStatus("Tiempo real activo");
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.event_type === "attendance_recent_update" && Array.isArray(payload.records)) {
            setRecords(payload.records);
          }
        } catch (error) {
          console.error("Error interpretando mensaje WS de registros:", error);
        }
      };

      socket.onerror = () => {
        setConnectionStatus("Reconectando...");
      };

      socket.onclose = () => {
        if (cancelled) return;
        setConnectionStatus("Reconectando...");
        reconnectTimeoutRef.current = window.setTimeout(connectSocket, 1500);
      };
    };

    loadInitialData();
    connectSocket();

    return () => {
      cancelled = true;
      if (reconnectTimeoutRef.current) window.clearTimeout(reconnectTimeoutRef.current);
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  return (
    <section className="recent-panel">
      <div className="recent-panel-header">
        <div>
          <h2>Últimos registros</h2>
          <p>Últimos 10 movimientos capturados</p>
        </div>
        <span className="ws-pill">{connectionStatus}</span>
      </div>

      <div className="recent-table-wrapper">
        <table className="recent-table">
          <thead>
            <tr>
              <th>Hora</th>
              <th>Usuario</th>
              <th>Tipo</th>
              <th>Conf.</th>
            </tr>
          </thead>
          <tbody>
            {sortedRecords.length === 0 && (
              <tr>
                <td colSpan="4" className="empty-row">
                  Sin registros todavía
                </td>
              </tr>
            )}

            {sortedRecords.map((record) => (
              <tr key={record.id_registro}>
                <td>{formatTime(record.fecha_hora)}</td>
                <td>
                  <strong>{record.nombre_usuario || "Usuario"}</strong>
                  {record.numero_empleado && <span>{record.numero_empleado}</span>}
                </td>
                <td>
                  <span className={`type-badge ${record.tipo_registro === "Salida" ? "exit" : "entry"}`}>
                    {record.tipo_registro}
                  </span>
                </td>
                <td>{formatConfidence(record.confianza_modelo)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default RecentAttendanceTable;
