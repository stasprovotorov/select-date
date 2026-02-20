import { createContext } from "react"

export type AuthState = { 
  isAuthenticated: boolean 
}

export const AuthContext = createContext<AuthState>({ 
  isAuthenticated: false 
})
