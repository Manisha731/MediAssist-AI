import { useState } from 'react';
import Login from './Login';
import Signup from './Signup';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

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

  return <div><h1>Welcome to MediAssist AI</h1></div>;
}

export default App;