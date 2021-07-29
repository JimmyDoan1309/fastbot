# Fastbot

A small framework to build conversation AI fast and easy to extend. 

This project was inspired by Rasa (in both functions and code organization). However I do make some changes that make RASA not suitable for my usecases.

Some of Fastbot's features:

- **Tensorflow is soft-required**:
  
  - You can use Fastbot with just basic ML models from sklearn. This change allow the package to be smaller. And for command-action kind of bot where you do not require SOTA level model, you really don't need a 300mb library as a dependency.

  - If you want to do SOTA and need Tensorflow (for intent classification). Fastbot offers **`KerasClassifier`** with **`build_model`** method expose for quick implementation. Or else you could write a new **`Component`** from scratch. The default model **`KerasClassifier`** use is a simple CNN.

  - **`KerasClassifier`** will required Tensorflow during the training phase. However, when the model is saved, it will saved to `tflite` format (tflite-runtime is also soft-required). Which allow the bot during the deployment phase to be much less resource intensive. (tflite runtime package size is only 1.5mb, compared to 300mb of Tensorflow). The only downside is that not all Tensorflow's operations is supported in tflite.

- **Decouple between intent classification and entity extraction**:

  - Unlike Rasa which extracts entities during the NLU phase and uses the extracted entities as feature for intent classification. Fastbot only extracts entities when needed (in **`InputsCollector`**). The reason for this change is because many "useful" entities extraction process is IO bounded. Ex: Duckling, Geo Parsing, (External API)... Having these Entity Extractors in the NLU make the bot really slow if everytime the user say something, the NLU need to go and try to fetch entities from some external sources even if these entities has nothing to do with the task at hand.

  - The only Entity Extractor component that still in the NLU phrase is **`CRFEntityExtractor`** which is not IO bounded and also need to train.

- **Stories are not necessary**:

  - Unlike Rasa which use stories as a way to guide the conversation flow which I think is brilliant and actually required to build bot that can handle complex conversation. The down side is that it's very unintuitive to handle some "trivial" flow. For example we have a flow for `booking airplane ticket`, and the user say *"I need to book ticket for `x` people"* where x can be any number. It's quite tricky to write a story to handle that case.

  - Instead, Fastbot mainly use what I call `Dialog Stack` which is a concept inspired by Microsoft Bot Framework which allow to pop and push one or more `nodes` freely during the conversation (A `node` represent a bot's action) . For the airplane ticket example above. All we need to do is extract the `number` of people, set a `counter = 0`, push the `booking ticket flow` on top of the stack - pop it out when done and increase `counter += 1`. At the end, having a node to check if `counter < number`, if so, push the `booking ticket flow` back on top of the stack again, or else, go the the confirmation flow or something. 

  - While not necessary, stories is still supported through Policy (the name is also copy from Rasa) because there are so many case where stories is still kind of the only way. Currently, Fastbot has **`SklearnPolicy`** for completely independent from Tensorflow, and a **`KerasPolicy`** which use a simple LSTM model.

- **One-size-fit-all InputsCollector:**

  - **`InputsCollector`** is very inspired by Rasa's Form. During my use of Rasa, I need to write so many forms and each one of them have need to have different logic to handle extract inputs from user. At the end, I almost always need to rewrite an entire `Rasa's FormAction` for each form I want which is getting annoying.

  - Fastbot solves this with **`InputsCollector`** which have all the options I think most people will need when the bot tries to collect information from users. Some of the config you can set is:

    - When to prompt / re-prompt
    - In what order to reprompt
    - Handle default value
    - Only apply default value after re-prompt fail x number of time
    - Always ask for each input instead of use information from the previous message because we don't trust ambiguity.
    - Hook custom input validation functions (run for each input)
    - Hook custom form validation function (run when collect all the required inputs)

  - Using Marshmarllow allow Fastbot to de-serialize a config file into a InputsCollection node, which make creating Node is super easy and customizable.
