import { useState } from 'react';
import Login from './Login';
import Signup from './Signup';
import UploadReport from './UploadReport';

function App() {
  const [acceptedDisclaimer, setAcceptedDisclaimer] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

  if (!acceptedDisclaimer) {
    return (
      <div style={{ maxWidth: 560, margin: '40px auto', padding: 16 }}>
        <h2>Before you continue</h2>
        <p>
          MediAssist AI gives AI-generated summaries and explanations for
          informational purposes only. It is not medical advice. Always consult
          a healthcare provider before making treatment decisions.
        </p>
        <button onClick={() => setAcceptedDisclaimer(true)}>I understand</button>
      </div>
    );
  }

  if (!isLoggedIn) {
    if (showSignup) {
      return (
        <div>
          <Signup onSignupSuccess={() => setShowSignup(false)} />
          <button onClick={() => setShowSignup(false)}>Already have an account? Login</button>
        </div>
      );
    }
    return (
      <div>
        <Login onLoginSuccess={() => setIsLoggedIn(true)} />
        <button onClick={() => setShowSignup(true)}>Need an account? Sign up</button>
      </div>
    );
  }

  return <UploadReport />;
}

export default App;