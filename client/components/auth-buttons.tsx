export default function SignOutButton() {
  return (
    <div className="flex justify-center my-6">
      <a
        href="/auth/logout"
        className="px-6 py-2 rounded-lg bg-gray-800 text-white font-semibold shadow-md hover:shadow-lg transition-all duration-200 active:scale-95 active:shadow-sm"
      >
        Sign Out
      </a>
    </div>
  );
}