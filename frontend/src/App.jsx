import { useEffect, useRef, useState } from 'react';
import './App.css';
import Login from './Login';
import Signup from './Signup';
import UploadReport from './UploadReport';

function App() {
  const [acceptedDisclaimer, setAcceptedDisclaimer] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [justSignedUp, setJustSignedUp] = useState(false);

  const screenRef = useRef(null);
  const isFirstRender = useRef(true);

  let screen;
  let content;

  if (!acceptedDisclaimer) {
    screen = 'disclaimer';
    content = (
      <div className="card">
        <h1 id="disclaimer-title">Before you continue</h1>
        <p className="lead">
          Please read this notice. It applies to everything MediAssist AI shows you.
        </p>
        <div
          className="disclaimer disclaimer--notice"
          role="note"
          aria-labelledby="disclaimer-title"
        >
          <svg className="notice-icon" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2" />
            <path d="M12 11v6M12 7.5v.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <p>
            MediAssist AI gives AI-generated summaries and explanations for
            informational purposes only. It is not medical advice. Always consult
            a healthcare provider before making treatment decisions.
          </p>
        </div>
        <button
          className="button button-primary button-block"
          onClick={() => setAcceptedDisclaimer(true)}
        >
          I understand
        </button>
      </div>
    );
  } else if (!isLoggedIn) {
    screen = showSignup ? 'signup' : 'login';
    content = showSignup ? (
      <Signup
        onSignupSuccess={() => {
          setJustSignedUp(true);
          setShowSignup(false);
        }}
        onSwitch={() => setShowSignup(false)}
      />
    ) : (
      <Login
        onLoginSuccess={() => setIsLoggedIn(true)}
        notice={justSignedUp ? 'Account created. Please log in.' : ''}
        onSwitch={() => {
          setJustSignedUp(false);
          setShowSignup(true);
        }}
      />
    );
  } else {
    screen = 'upload';
    content = <UploadReport />;
  }

  // Move focus to the new screen so keyboard and screen-reader users
  // aren't left on an element that was just removed.
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    screenRef.current?.focus();
  }, [screen]);

  return (
    <div className="page">
      <header className="page-header">
        <span className="brand">MediAssist AI</span>
      </header>
      <main className="page-shell screen" key={screen} ref={screenRef} tabIndex={-1}>
        {content}
      </main>
    </div>
  );
}

export default App;