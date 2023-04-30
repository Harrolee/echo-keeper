import React, { useState } from "react";
import axios from "axios";
import Settings from "../components/Settings";
import { supportedLanguages, modelOptions } from "../constants";
import withStyles from "@material-ui/core/styles/withStyles";
import { Button } from "react-bootstrap";

const BACKEND_URL = "http://127.0.0.1:8000";
const useStyles = () => ({
  settings: {
    display: "flex",
    width: "100%",
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
  const [projectName, setProjectName] = useState("");

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
          onNameProject={setProjectName}
        />
      </div>
      <Button onClick={startProject} variant="primary">
        Create Project
      </Button>
      <br></br>
      <Button onClick={() => onConfigure(true)} variant="success">
        Already set?
      </Button>
      <br></br>
      <Button
        onClick={() => {
          console.log(projectName);
        }}
        variant="secondary"
      >
        I have a Project
      </Button>
    </>
  );

  function startProject() {
    if (projectName === "") {
      alert("Please give your project a name");
      return;
    }

    const headers = {
      "content-type": "multipart/form-data",
    };
    const formData = new FormData();
    formData.append("language", selectedLanguage);
    formData.append("model_size", modelOptions[selectedModel]);
    formData.append("project_name", projectName);
    axios
      .post(`${BACKEND_URL}/start_project`, formData, { headers })
      .catch(function (error) {
        alert("Could not start project");
        console.log(error);
      })
      .then(() => {
        onConfigure(true);
      });
  }
};

export default withStyles(useStyles)(ProjectSetup);
