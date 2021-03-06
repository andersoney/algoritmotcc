/*
  This file implements a robot without coordination.
  The robot moves to the target using potential field and repels from another robot
  using this method.
*/

#include "wiseRobot.h"

#include "commonMethods.cpp"

//Constructor. pool is the message pool to send and receive msgs
WiseRobot::WiseRobot(Pool_t *pool) : connection(pool) {}

//Initialize all robot data (pose, connection, velocity, etc.)
void WiseRobot::init(int id)
{
    m_id = id;
    m_name = "robot" + intToStr(id);

    Pose pose = pos->GetPose();
    m_x = pose.x;
    m_y = pose.y;
    m_th = pose.a;
    estado = ENTRANDO;
    numIterations = numIterationsReachGoal = 0;

#ifdef GENERAL_LOG
    log.open(("logs/" + m_name).c_str());
#endif

    connection.init_connection(1);

    init_position_data();

    init_laser();

    finished = false;
    stalls = 0;
    alreadyStalled = false;
}

//Finish robot, freeing some variables and closing files
void WiseRobot::finish()
{
    cout << "Destroyed " << m_name << "!" << endl;
#ifdef GENERAL_LOG
    log.close();
#endif
}

//Alter the values of fx and fy, adding repulsion force.
void WiseRobot::obstaclesRepulsionForces(double &fx, double &fy)
{
    double Kobs = Ki; // Weight of the obstacle repulsion forces
    double distance;
    double dx = 0;
    double dy = 0;
    double fx_ = 0, fy_ = 0;
    std::vector<ModelRanger::Sensor> sensors = laser->GetSensors();
    ModelRanger::Sensor sensor = sensors[0];
    const std::vector<meters_t> &scan = sensor.ranges;
    uint32_t sample_count = scan.size();
    for (uint32_t i = 0; i < sample_count; i++)
    {
        distance = scan[i];
        double influence = INFLUENCE;
        if (distance <= influence)
        {
            dx = distance * cos(m_th + getBearing(i));
            dy = distance * sin(m_th + getBearing(i));
            if (dx < limit && dx >= 0)
                dx = limit;
            if (dx > -limit && dx < 0)
                dx = -limit;
            if (dy < limit && dy >= 0)
                dy = limit;
            if (dy > -limit && dy < 0)
                dy = -limit;
#ifdef mudancas
            double _fx = 0, _fy = 0;
            if (estado == ENTRANDO)
            {
                _fx = -Kobs * CONSTANTE_R * (1.0 / distance - 1.0 / (influence * 2)) * (1.0 / pow((double)distance, 2)) * (dx / distance);
                _fy = -Kobs * CONSTANTE_R * (1.0 / distance - 1.0 / (influence * 2)) * (1.0 / pow((double)distance, 2)) * (dy / distance);
            }
            else if (estado == SAINDO)
            {
                _fx = -Kobs * (1.0 / distance - 1.0 / (influence * 2)) * (1.0 / pow((double)distance, 2)) * (dx / distance);
                _fy = -Kobs * (1.0 / distance - 1.0 / (influence * 2)) * (1.0 / pow((double)distance, 2)) * (dy / distance);
            }
#else
            _fx = -Kobs * (1.0 / distance - 1.0 / (influence * 2)) * (1.0 / pow((double)distance, 2)) * (dx / distance);
            _fy = -Kobs * (1.0 / distance - 1.0 / (influence * 2)) * (1.0 / pow((double)distance, 2)) * (dy / distance);
#endif
            fx += _fx;
            fy += _fy;

            fx_ += _fx;
            fy_ += _fy;
        }
    }
#ifdef DEBUG_FORCES
    fv.setRepulsiveForces(fx_, fy_);
#endif
}

//Implements the main loop of robot.
//Also contain robot controller and
//probabilistic finite state machine codes
void WiseRobot::walk()
{
    double fx = 0;
    double fy = 0;
    double norm = 0;
    double angTarget;
    double linAccel;
    double rotAccel;

    numIterations++;

    //how many times robot stall?
    if (pos->Stalled())
    {
        if (!alreadyStalled)
        {
            stalls++;
            alreadyStalled = true;
        }
    }
    else
    {
        alreadyStalled = false;
    }

    Pose pose = pos->GetPose();
    m_x = pose.x;
    m_y = pose.y;
    m_th = pose.a;

    if (pho() < waypointDist)
    {
        finished = true;
        currentWaypoint = 1 + (rand() % NUMBER_OF_WAYPOINTS);
        estado = SAINDO;
        pos->SetColor(GOING_OUT_COLOR);

        numIterationsReachGoal = numIterations;
        numIterations = 0;
    }

    if (finished && (distance(m_x, m_y, waypoints[0][0], waypoints[0][1]) >= DISTANT_RADIUS))
    {
        connection.finish(m_id, numIterationsReachGoal, numIterations, stalls);
        pos->SetColor(Color(0, 0, 0));
        finish();
        finished = false;
    }

#ifdef CHECK_DEAD_ROBOTS
    if (numIterations > DEAD_ITERATIONS)
    {
        connection.finish(m_id, numIterations, 0, stalls);
        pos->SetColor(Color(0, 0, 0));
        finish();
    }
#endif

    destineX = waypoints[currentWaypoint][0];
    destineY = waypoints[currentWaypoint][1];

    fx = (destineX - m_x);
    fy = (destineY - m_y);
    norm = sqrt(pow(fx, 2) + pow(fy, 2));
#ifdef mudancas
    if (estado == ENTRANDO)
    {
        fx = Ka * fx / norm;
        fy = Ka * fy / norm;
    }
    else if (estado == SAINDO)
    {
        fx = CONSTANTE * Ka * fx / norm;
        fy = CONSTANTE * Ka * fy / norm;
    }
#else
    fx = Ka * fx / norm;
    fy = Ka * fy / norm;
#endif
#ifdef DEBUG_FORCES
    fv.setAttractiveForces(fx, fy);
#endif

    obstaclesRepulsionForces(fx, fy);

    saturation(fx, fy, maxForce);
#ifdef DEBUG_FORCES
    fv.setResultantForces(fx, fy);
#endif

    if (fx == 0 && fy == 0) // Change to inequalities?
        angTarget = m_th;
    else
        angTarget = atan2(fy, fx);

    linAccel = Kl * (fx * cos(m_th) + fy * sin(m_th));
    rotAccel = Kr * (angDiff(angTarget, m_th));

    linAccel += -Kdp * linSpeed;
    rotAccel += -Kdp * rotSpeed;

    linSpeed = linSpeed + linAccel * (TIME_STEP);
    rotSpeed = rotSpeed + rotAccel * (TIME_STEP);

    this->pos->SetXSpeed(linSpeed);
    this->pos->SetTurnSpeed(rotSpeed);

#ifdef GENERAL_LOG
    log << m_x << " " << m_y << " " << destineX << " " << destineY << " " << endl;
#endif
}

Pool_t pool;

//Pointer to a new robot.
//Every call of this library will create a new robot
//using this pointer.
WiseRobot *robot;

extern "C" int Init(Model *mod, CtrlArgs *args)
{
    robot = new WiseRobot(&pool);
    vector<string> tokens;
    Tokenize(args->worldfile, tokens);

    robot->pos = (ModelPosition *)mod;
    robot->pos->AddCallback(Model::CB_UPDATE, (model_callback_t)PositionUpdate, robot);
    robot->laser = (ModelRanger *)mod->GetChild("ranger:1");

    robot->laser->Subscribe(); // starts the laser updates
    robot->pos->Subscribe();   // starts the position updates

    robot->init(atoi(tokens[1].c_str()));
#ifdef DEBUG_FORCES
    robot->pos->AddVisualizer(&robot->fv, true);
#endif
    return 0;
}
