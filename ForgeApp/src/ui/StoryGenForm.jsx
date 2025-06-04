import ForgeUI, {
  useState,
  TextField,
  Button,
  Text,
  useEffect,
} from "@forge/ui";

const StoryGenForm = () => {
  const [input, setInput] = useState("");
  const [submitted, setSubmitted] = useState(false);

  return (
    <>
      <TextField label="Requirement" value={input} onChange={setInput} />
      <Button text="Generate" onClick={() => setSubmitted(true)} />
      {submitted && <Text>Generated stories would appear here (stub).</Text>}
    </>
  );
};

export default StoryGenForm;
