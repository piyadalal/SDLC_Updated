import ForgeUI, {
  render,
  Text,
  Fragment,
  TextField,
  Form,
  useState,
} from "@forge/ui";
import api from "@forge/api";

const App = () => {
  const [result, setResult] = useState(undefined);

  const onSubmit = async (formData) => {
    const res = await api.fetch("/api/storygen", {
      method: "POST",
      body: JSON.stringify({ requirement: formData.requirement }),
    });

    const data = await res.json();
    setResult(data.message);
  };

  return (
    <Fragment>
      {!result && (
        <Form onSubmit={onSubmit}>
          <TextField name="requirement" label="Enter Requirement" />
        </Form>
      )}
      {result && <Text>{result}</Text>}
    </Fragment>
  );
};

export const run = render(<App />);
