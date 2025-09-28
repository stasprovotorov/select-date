import Calendar from "@/components/calendar";
import AuthButton from "./auth-buttons";

export default function Home() {
  return (
    <main>
      <AuthButton />
      <Calendar />
    </main>
  );
}