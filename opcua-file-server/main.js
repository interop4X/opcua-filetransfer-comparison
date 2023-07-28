const { OPCUAServer, UAFile, Variant, DataType, StatusCodes } = require("node-opcua");
const { installFileType } = require("node-opcua-file-transfer");

// Create an instance of OPCUAServer
const createServer = async () => {
  const opcuaServer = new OPCUAServer({
    port: 4840, // Port of the listening socket of the server
    resourcePath: "", // This path will be added to the endpoint resource name
    buildInfo: {
      productName: "MySampleServer1",
      buildNumber: "7658",
      buildDate: new Date(2014, 5, 2),
    },
  });

  // Initialize the server
  await opcuaServer.initialize();
  console.log("Server initialized");

  return opcuaServer;
};

// Declare a new object
const declareObject = (opcuaServer) => {
  const addressSpace = opcuaServer.engine.addressSpace;
  const namespace = addressSpace.getOwnNamespace();

  return namespace.addObject({
    organizedBy: addressSpace.rootFolder.objects,
    browseName: "MyDevice",
  });
};

// Create instances of FileType for each test file
const createFileTypeInstance = (fileType, fileName, addressSpace) => {
  return fileType.instantiate({
    nodeId: `s=${fileName}`,
    browseName: fileName,
    organizedBy: addressSpace.rootFolder.objects,
  });
};

// Bind the OPCUAFile object with our files
const bindFile = (fileTypeInstance, fileName) => {
  installFileType(fileTypeInstance, { filename: `../data/${fileName}` });
};

// Start the server
const startServer = (opcuaServer) => {
  opcuaServer.start(() => {
    console.log("Server is now listening ... (press CTRL+C to stop)");
    console.log("Port ", opcuaServer.endpoints[0].port);
    const endpointUrl = opcuaServer.endpoints[0].endpointDescriptions()[0].endpointUrl;
    console.log("The primary server endpoint URL is ", endpointUrl);
  });
};

(async () => {
  const opcuaServer = await createServer();
  declareObject(opcuaServer);

  const addressSpace = opcuaServer.engine.addressSpace;
  const fileType = addressSpace.findObjectType("FileType");

  // Define file names
  const smallTestFile = "test_1m.data";
  //const mediumTestFile = "test_100m.data";
  //const largeTestFile = "test_1000m.data";

  // Create and bind each file
  bindFile(createFileTypeInstance(fileType, smallTestFile, addressSpace), smallTestFile);
  //bindFile(createFileTypeInstance(fileType, mediumTestFile, addressSpace), mediumTestFile);
  //bindFile(createFileTypeInstance(fileType, largeTestFile, addressSpace), largeTestFile);

  // Start the server
  startServer(opcuaServer);
})();
