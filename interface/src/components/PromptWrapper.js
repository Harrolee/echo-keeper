import React from "react";
import withStyles from "@material-ui/core/styles/withStyles";

const useStyles = () => ({
  prompt: {
    marginTop: "20px",
  },
});

const PromptWrapper = ({ classes, prompt, children }) => {
  return (
    <>
      {children}
      <br />
      <div className={classes.prompt}>{prompt}</div>
    </>
  );
};

export default withStyles(useStyles)(PromptWrapper);
