import Calendar from "@/components/calendar"
import Auth from "@/components/auth"
import SignOutButton from "@/components/auth-buttons"
import Sync from "@/components/sync"

export default function Home() {
  return (
    <Auth>
      <Sync>
        <main>
          <SignOutButton />
          <Calendar />
        </main>
      </Sync>
    </Auth>
  );
}
