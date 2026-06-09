import MapView from "./components/MapView";
import Login from "./components/Login";

import "./App.css";

function App() {
  const token = localStorage.getItem("token");

  return <>{!token ? <Login /> : <MapView />}</>;
}

export default App;
