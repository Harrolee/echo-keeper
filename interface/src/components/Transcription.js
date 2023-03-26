import React from "react";
import withStyles from "@material-ui/core/styles/withStyles";
import { Button } from "react-bootstrap";

const useStyles = () => ({});

const Transcription = ({ classes, transcribedText, updateTranscription }) => {
  function handleSubmit(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    updateTranscription(formData);
  }

  return (
    <form method="post" onSubmit={handleSubmit}>
      <Button type="submit" variant="success">
        Save transcription
      </Button>
      <br />
      <textarea
        name="reviewedTranscription"
        defaultValue={transcribedText}
        rows={2}
        columns={100}
      />
    </form>
  );
};

export default withStyles(useStyles)(Transcription);
