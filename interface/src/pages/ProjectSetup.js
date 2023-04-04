import React, { useState } from "react";
import axios from "axios";
import Settings from "../components/Settings";
import { supportedLanguages, modelOptions } from "../constants";
import withStyles from "@material-ui/core/styles/withStyles";
import { Button } from "react-bootstrap";

const BACKEND_URL = "http://127.0.0.1:8000";
const useStyles = () => ({
  settings: {
    marginBottom: "20px",
    display: "flex",
    width: "100%",
  },
  buttonsSection: {
    marginBottom: "40px",
  },
});

const ProjectSetup = ({
  classes,
  isTranscribing,
  isRecording,
  onConfigure,
}) => {
  const [selectedModel, setSelectedModel] = useState(1);
  const [selectedLanguage, setSelectedLanguage] = useState("english");

  // const selectedLangRef = useRef(selectedLanguage);
  // selectedLangRef.current = selectedLanguage;

  // const selectedModelRef = useRef(selectedModel);
  // selectedModelRef.current = selectedModel;

  return (
    <>
      <div className={classes.settings}>
        <Settings
          disabled={isTranscribing || isRecording}
          possibleLanguages={supportedLanguages}
          selectedLanguage={selectedLanguage}
          onLanguageChange={setSelectedLanguage}
          modelOptions={modelOptions}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
        />
      </div>
      <div className={classes.buttonsSection}>
        <Button onClick={startProject} variant="primary">
          Create Project
        </Button>
        <br></br>
        <Button onClick={onConfigure(true)} variant="success">
          Already set?
        </Button>
      </div>
    </>
  );

  function startProject() {
    const headers = {
      "content-type": "multipart/form-data",
    };
    const formData = new FormData();
    formData.append("language", selectedLanguage);
    formData.append("model_size", modelOptions[selectedModel]);
    axios
      .post(`${BACKEND_URL}/start_project`, formData, { headers })
      .then(() => {
        onConfigure(true);
      });
  }
};

export default withStyles(useStyles)(ProjectSetup);
