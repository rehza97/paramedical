import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import PromotionsPage from "./pages/PromotionsPage";
import ServicesPage from "./pages/ServicesPage";
import SpecialitiesPage from "./pages/SpecialitiesPage";
import PlanningsPage from "./pages/PlanningsPage";
import StudentSchedulesPage from "./pages/StudentSchedulesPage";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-blue-600 text-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between items-center py-4">
              <h1 className="text-2xl font-bold">
                Gestion des Stages Paramédicaux
              </h1>
              <div className="flex space-x-4">
                <Link
                  to="/promotions"
                  className="px-4 py-2 rounded-lg transition-colors bg-blue-500 hover:bg-blue-700"
                >
                  Promotions
                </Link>
                <Link
                  to="/services"
                  className="px-4 py-2 rounded-lg transition-colors bg-blue-500 hover:bg-blue-700"
                >
                  Services
                </Link>
                <Link
                  to="/specialities"
                  className="px-4 py-2 rounded-lg transition-colors bg-blue-500 hover:bg-blue-700"
                >
                  Spécialités
                </Link>
                <Link
                  to="/plannings"
                  className="px-4 py-2 rounded-lg transition-colors bg-blue-500 hover:bg-blue-700"
                >
                  Plannings
                </Link>
                <Link
                  to="/student-schedules"
                  className="px-4 py-2 rounded-lg transition-colors bg-blue-500 hover:bg-blue-700"
                >
                  Plannings Étudiants
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto py-8 px-4">
          <Routes>
            <Route path="/promotions" element={<PromotionsPage />} />
            <Route path="/services" element={<ServicesPage />} />
            <Route path="/specialities" element={<SpecialitiesPage />} />
            <Route path="/plannings" element={<PlanningsPage />} />
            <Route
              path="/student-schedules"
              element={<StudentSchedulesPage />}
            />
            <Route path="*" element={<PromotionsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
