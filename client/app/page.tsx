import Calendar from "@/components/calendar";
import AuthButton from "./auth_button";

export default function Home() {
  return (
    <main>
      <AuthButton />
      <Calendar />
    </main>
  );
}