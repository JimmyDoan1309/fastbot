import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import "./App.css";
import { BotFlowPage, HomePage } from "./pages";

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/home">
          <HomePage />
        </Route>
        <Route path="/bot/:id/workflow">
          <BotFlowPage />
        </Route>
        <Route path="/">
          <HomePage />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
