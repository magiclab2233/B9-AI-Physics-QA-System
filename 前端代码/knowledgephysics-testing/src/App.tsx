import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { APP_BASE_PATH } from './config/paths';
import './App.css';
import Content from './widgets/Content';

function App() {
  return (
    <Router basename={APP_BASE_PATH}>
      <div className="min-h-screen w-screen bg-gray-100">
        <Routes>
          <Route path="/" element={<Content />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

