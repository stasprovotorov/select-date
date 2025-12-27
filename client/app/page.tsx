import Calendar from "@/components/calendar"
import AuthGate from "@/components/AuthGate"
import SignOutButton from "@/components/auth-buttons"
import Sync from "@/components/sync"

export default function Home() {
  return (
    <AuthGate>
      <Sync>
        <main>
          <SignOutButton />
          <Calendar />
        </main>
      </Sync>
    </AuthGate>
  );
}
