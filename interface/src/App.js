import React, { useState, useRef } from "react";
import { Button } from "react-bootstrap";
import withStyles from "@material-ui/core/styles/withStyles";
import Typography from "@material-ui/core/Typography";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import { ReactMic } from "react-mic";
import axios from "axios";
import Transcription from "./components/Transcription";
import ProjectSetup from "./pages/ProjectSetup";

const useStyles = () => ({
  root: {
    display: "flex",
    flex: "1",
    margin: "100px 0px 100px 0px",
    alignItems: "center",
    textAlign: "center",
    flexDirection: "column",
  },
  title: {
    marginBottom: "30px",
  },
  buttonsSection: {
    marginBottom: "40px",
  },
  recordIllustration: {
    width: "100px",
  },
});

const BACKEND_URL = "http://0.0.0.0:8000";

const App = ({ classes }) => {
  const [transcribedData, setTranscribedData] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isCorrecting, setIsCorrecting] = useState(false);
  const [isIdle, setIsIdle] = useState(true);
  const [isConfigured, setConfigured] = useState(false);

  const [stopTranscriptionSession, setStopTranscriptionSession] =
    useState(false);

  const stopTranscriptionSessionRef = useRef(stopTranscriptionSession);
  stopTranscriptionSessionRef.current = stopTranscriptionSession;

  // useEffect(() => {
  //   setIsCorrecting((!isRecording || !isTranscribing) && !isIdle);
  //   setIsIdle(!isRecording && !isTranscribing && !isCorrecting);
  //   console.log(`isIdle: ${isIdle} ----- isCorrecting: ${isCorrecting}`);
  // }, [isCorrecting, isIdle, isRecording, isTranscribing]);

  function startRecording() {
    setStopTranscriptionSession(false);
    setIsRecording(true);
    setIsIdle(false);
  }

  function stopRecording() {
    setStopTranscriptionSession(true);
    setIsRecording(false);
    // setIsTranscribing(false);
  }

  function onData(recordedBlob) {
    // console.log('chunk of real-time data is: ', recordedBlob);
  }

  function onStop(recordedBlob) {
    saveRecordingAndKeepPath(recordedBlob);
    setIsTranscribing(true);
  }

  function saveRecordingAndKeepPath(recordedBlob) {
    const headers = {
      "content-type": "multipart/form-data",
    };
    const formData = new FormData();
    formData.append("audio_data", recordedBlob.blob, "temp_recording");
    axios
      .post(`${BACKEND_URL}/save_audio`, formData, { headers })
      .then((res) => {
        const { text } = res.data;
        setTranscribedData(() => [text]);
        setIsTranscribing(false);
        setIsCorrecting(true);
      });

    if (!stopTranscriptionSessionRef.current) {
      setIsRecording(true);
    }
  }

  function updateTranscription(formData) {
    const headers = {
      "content-type": "multipart/form-data",
    };
    axios.post(`${BACKEND_URL}/save_transcription`, formData, { headers });

    setIsIdle(true);
    setIsCorrecting(false);
  }

  return (
    <div className={classes.root}>
      <div className={classes.title}>
        <Typography variant="h3">
          <span role="img" aria-label="monkey-emoji">
            🙉
          </span>{" "}
          Echo Keeper{" "}
          <span role="img" aria-label="monkey-emoji">
            🙉
          </span>
        </Typography>
      </div>

      {!isConfigured ? (
        <ProjectSetup
          onConfigure={setConfigured}
          isTranscribing={isTranscribing}
          isRecording={isRecording}
        />
      ) : (
        <>
          <div className={classes.buttonsSection}>
            {!isRecording && !isTranscribing && isIdle && (
              <Button onClick={startRecording} variant="primary">
                Start transcribing
              </Button>
            )}
            {(isRecording || isTranscribing) && (
              <Button
                onClick={stopRecording}
                variant="danger"
                disabled={stopTranscriptionSessionRef.current}
              >
                Stop
              </Button>
            )}
          </div>

          <div className="recordIllustration">
            {!isCorrecting && (
              <ReactMic
                record={isRecording}
                className="sound-wave"
                onStop={onStop}
                onData={onData}
                strokeColor="#0d6efd"
                backgroundColor="#f6f6ef"
              />
            )}
            {isCorrecting && (
              <Transcription
                transcribedText={transcribedData}
                updateTranscription={updateTranscription}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default withStyles(useStyles)(App);
