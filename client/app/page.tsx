import Calendar from "@/components/calendar";

export default function Home() {
  return (
    <main>
      <a href="/auth/login">Login</a>
      <a href="/auth/logout">Logout</a>
      <Calendar />
    </main>
  );
}