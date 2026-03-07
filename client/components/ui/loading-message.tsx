export default function loadingMessage(text: string) {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <p
        className="font-sans text-4xl font-bold"
        style={{ color: "#A6A6A6" }}
        role="status"
        aria-live="polite"
      >
        {text}
      </p>
    </div>
  )  
}
