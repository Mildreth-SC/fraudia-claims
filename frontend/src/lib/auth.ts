// FraudIA Authentication System
// Credenciales demo para hackathon

export interface User {
  id: string;
  email: string;
  name: string;
  role: "analista" | "admin" | "jurado";
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
}

// Credenciales de demostración (hardcodeadas para hackathon)
const DEMO_CREDENTIALS = [
  {
    email: "analista@aseguradoradelsur.com",
    password: "FraudIA2026",
    name: "Analista Antifraude",
    role: "analista" as const,
    id: "analista-001"
  },
  {
    email: "admin@aseguradoradelsur.com",
    password: "Admin2026",
    name: "Administrador",
    role: "admin" as const,
    id: "admin-001"
  },
  {
    email: "jurado@hackiathon.com",
    password: "Demo2026",
    name: "Jurado Hackathon",
    role: "jurado" as const,
    id: "jurado-001"
  }
];

// Validar credenciales
export function validateCredentials(email: string, password: string): User | null {
  const credential = DEMO_CREDENTIALS.find(
    c => c.email === email && c.password === password
  );

  if (!credential) {
    return null;
  }

  return {
    id: credential.id,
    email: credential.email,
    name: credential.name,
    role: credential.role
  };
}

// Persistencia en localStorage
const AUTH_STORAGE_KEY = "fraudia_auth";

export function saveAuthToStorage(user: User): void {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
}

export function loadAuthFromStorage(): User | null {
  try {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

export function clearAuthFromStorage(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY);
}
