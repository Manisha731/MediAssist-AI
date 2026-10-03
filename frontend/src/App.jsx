import { useEffect, useRef, useState } from 'react';
import './App.css';
import Login from './Login';
import Signup from './Signup';
import UploadReport from './UploadReport';

function App() {
  const [acceptedDisclaimer, setAcceptedDisclaimer] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

  const screenRef = useRef(null);
  const isFirstRender = useRef(true);

  let screen;
  let content;

  if (!acceptedDisclaimer) {
    screen = 'disclaimer';
    content = (
      <div>
        <h2>Before you continue</h2>
        <p>
          MediAssist AI gives AI-generated summaries and explanations for
          informational purposes only. It is not medical advice. Always consult
          a healthcare provider before making treatment decisions.
        </p>
        <button onClick={() => setAcceptedDisclaimer(true)}>I understand</button>
      </div>
    );
  } else if (!isLoggedIn) {
    screen = showSignup ? 'signup' : 'login';
    content = showSignup ? (
      <div>
        <Signup onSignupSuccess={() => setShowSignup(false)} />
        <button onClick={() => setShowSignup(false)}>Already have an account? Login</button>
      </div>
    ) : (
      <div>
        <Login onLoginSuccess={() => setIsLoggedIn(true)} />
        <button onClick={() => setShowSignup(true)}>Need an account? Sign up</button>
      </div>
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