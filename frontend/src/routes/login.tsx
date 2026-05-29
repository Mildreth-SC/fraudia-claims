import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useAuth } from "./__root";
import { Login } from "@/components/fraudia/Login";
import { useEffect } from "react";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Login - FraudIA | Aseguradora del Sur" },
      {
        name: "description",
        content: "Sistema FraudIA - Acceso de usuarios autorizados",
      },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();

  // Si ya estás logueado, redirige al dashboard
  useEffect(() => {
    if (user) {
      navigate({ to: "/" });
    }
  }, [user, navigate]);

  return <Login onLoginSuccess={login} />;
}
