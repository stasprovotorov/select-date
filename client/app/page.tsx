import Calendar from "@/components/calendar";
import AuthButton from "./auth_button";

export default function Home() {
  return (
    <main>
      <h1>Добро пожаловать!</h1>
      <AuthButton />
      <Calendar />
    </main>
  );
}