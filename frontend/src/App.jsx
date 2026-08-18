import { useState } from 'react';
import Login from './Login';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  if (!isLoggedIn) {
    return <Login onLoginSuccess={() => setIsLoggedIn(true)} />;
  }

  return <div><h1>Welcome to MediAssist AI</h1></div>;
}

export default App;