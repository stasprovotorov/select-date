"use client";

export default function AuthButton() {
  return (
    <div className="auth-btn-wrapper">
      <a href="/auth/login" style={{ textDecoration: "none" }}>
        <button className="auth-btn">Sign in</button>
      </a>
      <style jsx>{`
        .auth-btn-wrapper {
          display: flex;
          justify-content: center;
          align-items: flex-start;
          margin-top: 1cm;
          margin-bottom: 2rem;
        }
        .auth-btn {
          background: #444; /* более серый */
          color: #fff;
          font-size: 1.2rem;
          padding: 0.8em 2.2em;
          border: none;
          border-radius: 0.7em;
          cursor: pointer;
          box-shadow: 0 2px 10px rgba(0,0,0,0.10);
          transition: 
            transform 0.08s, 
            box-shadow 0.15s, 
            background 0.2s;
        }
        .auth-btn:active {
          transform: translateY(2px) scale(0.97);
          box-shadow: 0 1px 4px rgba(0,0,0,0.07);
          background: #222; /* темнее при нажатии */
        }
        .auth-btn:hover {
          box-shadow: 0 4px 18px rgba(0,0,0,0.18);
          background: #333; /* чуть темнее при наведении */
        }
      `}</style>
    </div>
  );
}