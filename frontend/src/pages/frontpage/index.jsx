import React from "react";
import { Redirect } from "react-router-dom";
function FrontPage() {
  return (
    <>
      <Redirect to={"/bill/116/Senate/47/ENR/diffs/54/200306"} />
    </>
  );
}

export default FrontPage;
