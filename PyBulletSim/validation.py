import pybullet as p
import csv
import pybullet_data
import numpy as np

#Define the object and parameter method (Trajectory (Traj) or Velocity (Vel))
object = "Box007"
param = "Vel"

if object == "Box004" and param == "Traj":
    mu = 0.4
    eN = 0.1
elif object == "Box004" and param == "Vel":
    mu = 0.65
    eN = 0.35
elif object == "Box005" and param == "Traj":
    mu = 0.45
    eN = 0.15
elif object == "Box005" and param == "Vel":
    mu = 0.45
    eN = 0.35
elif object == "Box006" and param == "Traj":
    mu = 0.35
    eN = 0.4
elif object == "Box006" and param == "Vel":
    mu = 0.25
    eN = 0.35
elif object == "Box007" and param == "Traj":
    mu = 0.35
    eN = 0.40
elif object == "Box007" and param == "Vel":
    mu = 0.35
    eN = 0.50
else:
    raise Exception("Combination of object and param is not supported.") 


#Import states from csv file. Each row has the structure [startPos[x,y,z] startOrientation[x,y,z,w] linearVelocity[x,y,z] angularVelocity[x,y,z] planePos[x,y,z] planeOrientation[x,y,z,w]] 
path = 'simstates/' + object + '_' + param + '/validation_states.csv'

#Total number of simulations
with open(path,'r') as f:
    Nsim = sum(1 for line in f)


with open(path,'r') as box_states:
    boxstates = csv.reader(box_states, quoting=csv.QUOTE_NONNUMERIC)

    #Index to keep count of the number of simulations
    sim_idx = 1

    #Create a csv file to write the simulation data too
    CSV_PATH = 'simstates/' + object + '_' + param + '/sim_results/validation/validation_results.csv'
    f = open(CSV_PATH, 'w', newline='')
    writer = csv.writer(f)

    #Loop through the states
    for row in boxstates:

        #Connect to the BULLET physics client (p.GUI for graphical interface, p.DIRECT for non-graphical version)
        physicsClient = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally

        #Set the gravity
        p.setGravity(0,0,-9.81) 

        #Define the camera settings (for visualization only)
        cam = p.getDebugVisualizerCamera()
        p.resetDebugVisualizerCamera(cameraYaw = cam[8], cameraPitch = -15, cameraTargetPosition = [0,0,0],cameraDistance =1.6)

        #General settings
        p.setPhysicsEngineParameter(useSplitImpulse = 1) #this should prevent compensations due to penetrations 
        p.setTimeStep(1/360) #set the timestep
        Ntimeidx = 700 #run 700 timesteps

        # Set the box initial position, orientation, lin velocity, and angular velocity
        startPos = [row[0],row[1],row[2]] #[x,y,z]
        startOrientation = [row[3],row[4],row[5],row[6]] # [x,y,z,w] quaternion
        linearVelocity = [row[7],row[8],row[9]]
        angularVelocity = [row[10],row[11],row[12]]

        # Set contact plane base position and orientation
        planePos = [row[13],row[14],row[15]]
        planeOrientation =  [row[16],row[17],row[18],row[19]]

        # Load the box and assign initial pose, velocity, and coefficients
        urdf = "urdf/" + object + ".urdf"
        boxId = p.loadURDF(urdf,startPos, startOrientation)
        p.resetBaseVelocity(boxId,linearVelocity,angularVelocity)
        p.changeDynamics(boxId,-1,restitution=eN,lateralFriction=mu)


        # Define the contact plane dimensions, collisionshape, position and orientation.
        planeL, planeW, planeH = 20,20,0
        sh_colPlane1 = p.createCollisionShape(p.GEOM_BOX,halfExtents=[planeL,planeW,planeH])
        plane1 = p.createMultiBody(baseMass=0,baseCollisionShapeIndex=sh_colPlane1,basePosition=planePos,baseOrientation=planeOrientation)
        p.changeDynamics(plane1,-1,restitution=1,lateralFriction=1)
        p.changeVisualShape(plane1, -1, rgbaColor=[150/255, 150/255, 150/255, 1])

        #Simulate
        for i in range (Ntimeidx):    
            #Write box position and orientation to file
            cubePos, cubeOrn = p.getBasePositionAndOrientation(boxId)
            cubeLin, cubeAng = p.getBaseVelocity(boxId)
            rowBox = [cubePos[0], cubePos[1], cubePos[2], cubeOrn[0], cubeOrn[1], cubeOrn[2], cubeOrn[3], cubeLin[0], cubeLin[1], cubeLin[2], cubeAng[0], cubeAng[1],cubeAng[2]]
            writer.writerow(rowBox)
            p.stepSimulation() 
        p.disconnect()                

        #Print the current status
        print("Completed simulation " + str(sim_idx) + " out of " + str(Nsim) + ".")

        #Update the index
        sim_idx = sim_idx +1

    #Close the CSV file    
    f.close()