import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
export const API_URL = "http://localhost:8000/api/students/";
import "bootstrap/dist/css/bootstrap.min.css";

ReactDOM.render(
<React.StrictMode>
	<App />
</React.StrictMode>,
document.getElementById("root")
);
