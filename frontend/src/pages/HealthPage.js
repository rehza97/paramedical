import React, { useState, useEffect } from "react";
import { healthCheck } from "../services/api";
import Message from "../components/Message";
import { useMessage } from "../contexts/MessageContext";

const HealthPage = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [lastCheck, setLastCheck] = useState(null);
  const { message, type, showMessage, loading, setLoading } = useMessage();

  const checkHealth = async () => {
    try {
      setLoading(true);
      const { data } = await healthCheck();
      setHealthStatus(data);
      setLastCheck(new Date().toLocaleString());
      showMessage("Statut de santé vérifié avec succès");
    } catch (error) {
      showMessage("Erreur lors de la vérification du statut de santé", "error");
      setHealthStatus({ status: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Statut de Santé de l'API</h2>
      <Message text={message} type={type} />

      <div className="mb-6">
        <button
          onClick={checkHealth}
          className="bg-blue-600 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          {loading ? "Vérification..." : "Vérifier le Statut"}
        </button>
        {lastCheck && (
          <span className="ml-4 text-gray-600">
            Dernière vérification: {lastCheck}
          </span>
        )}
      </div>

      {healthStatus && (
        <div className="bg-white rounded shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Statut du Service</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="font-medium">Statut:</span>
              <span
                className={`ml-2 px-2 py-1 rounded text-sm ${
                  healthStatus.status === "healthy"
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {healthStatus.status}
              </span>
            </div>
            {healthStatus.service && (
              <div>
                <span className="font-medium">Service:</span>
                <span className="ml-2 text-gray-700">
                  {healthStatus.service}
                </span>
              </div>
            )}
            {healthStatus.message && (
              <div className="md:col-span-2">
                <span className="font-medium">Message:</span>
                <span className="ml-2 text-gray-700">
                  {healthStatus.message}
                </span>
              </div>
            )}
          </div>

          <div className="mt-4 p-3 bg-gray-100 rounded">
            <h4 className="font-medium mb-2">Réponse complète:</h4>
            <pre className="text-sm overflow-auto">
              {JSON.stringify(healthStatus, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default HealthPage;
