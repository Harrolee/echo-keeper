import React, { useEffect, useState } from "react";
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
  const [isCreateMode, setCreateMode] = useState(true);
  const [selectedModel, setSelectedModel] = useState(1);
  const [selectedLanguage, setSelectedLanguage] = useState("english");
  const [selectedProject, setSelectedProject] = useState("");
  const [projectName, setProjectName] = useState("");
  const [existingProjects, setExistingProjects] = useState([]);

  const handleModeChange = () => {
    if (isCreateMode) {
      setCreateMode(false);
    } else {
      setCreateMode(true);
    }
  };

  const handleStartRecording = () => {
    if (isCreateMode) {
      createProject();
    } else {
      loadProject();
    }
  };

  useEffect(() => {
    axios
      .get(`${BACKEND_URL}/projects`)
      .catch(function (error) {
        alert("Could not load projects");
        console.log(error);
      })
      .then((res) => {
        if (res.data.length === 0) {
          setSelectedProject("No projects found");
        } else {
          setExistingProjects(res.data);
          setSelectedProject(existingProjects[0]);
        }
      });
  }, []);

  return (
    <>
      <div className={classes.settings}>
        <Settings
          newProject={isCreateMode}
          disabled={isTranscribing || isRecording}
          possibleLanguages={supportedLanguages}
          selectedLanguage={selectedLanguage}
          onLanguageChange={setSelectedLanguage}
          onProjectNameChange={setSelectedProject}
          selectedProject={selectedProject}
          existingProjects={existingProjects}
          modelOptions={modelOptions}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
          onNameProject={setProjectName}
        />
      </div>
      <Button onClick={handleModeChange} variant="primary">
        {isCreateMode ? "Load" : "Create"} Project
      </Button>
      <br></br>
      <Button onClick={handleStartRecording} variant="success">
        Start Recording
      </Button>
    </>
  );

  function loadProject() {
    const headers = {
      "content-type": "multipart/form-data",
    };
    const formData = new FormData();
    formData.append("language", selectedLanguage);
    formData.append("model_size", modelOptions[selectedModel]);
    formData.append("project_name", selectedProject);
    axios
      .post(`${BACKEND_URL}/load_project`, formData, { headers })
      .catch(function (error) {
        alert("Could not load project");
        console.log(error);
      })
      .then(() => {
        onConfigure(true);
      });
  }

  function createProject() {
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
