import {DotLoader } from "react-spinners";
function Spinner() {
  return (
    <div className="sweet-loading">
      <DotLoader
        color={"#22c55e"}
        size={150}
        aria-label="Loading Spinner"
        data-testid="loader"
      />
    </div>
  );
}

export default Spinner;