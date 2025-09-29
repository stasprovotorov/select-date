import Calendar from "@/components/calendar";
import AuthGate from "@/components/AuthGate";

export default function Home() {
  return (
    <AuthGate>
      <main>
        <Calendar />
      </main>
    </AuthGate>
  );
}