import Calendar from "@/components/calendar";
import AuthGate from "@/components/AuthGate";
import SignOutButton from "@/components/auth-buttons";

export default function Home() {
  return (
    <AuthGate>
      <main>
        <SignOutButton />
        <Calendar />
      </main>
    </AuthGate>
  );
}