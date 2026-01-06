import { createContext } from "react"

export type AuthState = { 
  isAuthenticated: boolean, 
  user: any | null 
}

export const AuthContext = createContext<AuthState>({ 
  isAuthenticated: false, 
  user: null 
})
