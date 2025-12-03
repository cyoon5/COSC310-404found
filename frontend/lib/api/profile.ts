// frontend/lib/api/profile.ts
import { apiClient } from "@/lib/apiClient";

export interface ChangePasswordRequest {
  username: string;
  old_password: string;
  new_password: string;
}

export interface UpdateBioRequest {
  username: string;
  bio: string;
}

export interface ChangeUsernameRequest {
  newUsername: string;
}

export async function changePassword(payload: ChangePasswordRequest) {
  // backend: POST /auth/change-password
  return apiClient.post<{ message: string; username: string }>(
    "/auth/change-password",
    payload
  );
}

export async function updateBio(payload: UpdateBioRequest) {
  // backend: POST /auth/update-bio
  return apiClient.post<{ message: string; username: string; bio: string }>(
    "/auth/update-bio",
    payload
  );
}

export async function changeUsername(payload: ChangeUsernameRequest) {
  // backend: POST /auth/change-username
  return apiClient.post<{ message: string; newUsername: string }>(
    "/auth/change-username",
    payload
  );
}
