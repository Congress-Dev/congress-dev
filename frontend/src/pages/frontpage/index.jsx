import React from "react";
import { Redirect } from "react-router-dom";
function FrontPage() {
  return (
    <>
      <Redirect to={"/bills"} />
    </>
  );
}

export default FrontPage;
