import Calendar from "@/components/calendar";
import { SignInButton, SignOutButton} from "./auth-buttons";

export default function Home() {
  return (
    <main>
      <SignInButton />
      <SignOutButton />
      <Calendar />
    </main>
  );
}