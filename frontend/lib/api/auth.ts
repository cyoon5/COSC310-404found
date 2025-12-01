import { apiClient, setSession, Session } from "@/lib/apiClient";

interface RegisterRequest {
  username: string;
  password: string;
}

interface RegisterResponse {
  message: string;
  user: any;
}

interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  message: string;
  role: "user" | "admin";
}

export async function registerUser(payload: RegisterRequest) {
  return apiClient.post<RegisterResponse>("/auth/register", payload);
}

export async function loginUser(payload: LoginRequest): Promise<Session> {
  const res = await apiClient.post<LoginResponse>("/auth/login", payload);
  const session: Session = { username: payload.username, role: res.role };
  setSession(session);
  return session;
}
