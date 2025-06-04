import ForgeUI, { render, Fragment, Macro, Text } from "@forge/ui";
import StoryGenForm from "./ui/StoryGenForm";

const App = () => (
  <Fragment>
    <Text>🧠 AI Story Generator</Text>
    <StoryGenForm />
  </Fragment>
);

export const run = render(<Macro app={<App />} />);