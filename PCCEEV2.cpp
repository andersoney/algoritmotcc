/*
  This file implements a robot without coordination.
  The robot moves to the target using potential field and repels from another robot
  using this method.
*/

#include "PCCEEV2.h"

// Constructor. pool is the message pool to send and receive msgs
PCCEEV2::PCCEEV2(Pool_t *pool) : connection(pool)
{
}

// Initialize all robot data (pose, connection, velocity, etc.)
void PCCEEV2::init(int id, int numRobots, int numExp, double distant_radius_to_finish_in, string patch)
{
    m_id = id;
    m_name = "robot" + intToStr(id);
    Pose pose = pos->GetPose();
    m_x = pose.x;
    m_y = pose.y;
    m_th = pose.a;
    estado = ENTRANDO;
    distant_radius_to_finish = distant_radius_to_finish_in;
    numIterations = numIterationsReachGoal = 0;

#ifdef GENERAL_LOG
    log.open(("logs/" + m_name).c_str());
#endif

    // connection.init_connection("saidas", numRobots, numExp);

    std::string h = patch + "/nRobots";
    h += std::to_string(numRobots) + "/logs_";
    h += std::to_string(numExp);
    FinalLog::init(h);

    init_position_data();

    init_laser();

    finished = false;
    stalls = 0;
    alreadyStalled = false;
}

// Finish robot, freeing some variables and closing files
void PCCEEV2::finish()
{
    // cout << "Destroyed " << m_name << "!" << endl;
#ifdef TELEPORT_ON_FINISH
    Pose p(1000.0, 1000.0, 0.0, 0.0);
    pos->SetPose(p);
    pos->Disable();
#endif
#ifdef GENERAL_LOG
    log.close();
#endif
}

// Alter the values of fx and fy, adding repulsion force.
void PCCEEV2::obstaclesRepulsionForces(double &fx, double &fy)
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
    double min_distance = 180;

    for (uint32_t i = 0; i < sample_count; i++)
    {
        distance = scan[i];
        if (min_distance > distance)
        {
            min_distance = distance;
        }
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
                _fx = -Kobs * CONSTANTE_R * multiplicador_repulsao * (1.0 / distance - 1.0 / (influence * 2)) * (1.0 / pow((double)distance, 2)) * (dx / distance);
                _fy = -Kobs * CONSTANTE_R * multiplicador_repulsao * (1.0 / distance - 1.0 / (influence * 2)) * (1.0 / pow((double)distance, 2)) * (dy / distance);
            }
            else if (estado == SAINDO)
            {
                _fx = -Kobs * multiplicador_repulsao * (1.0 / distance - 1.0 / (influence * 2)) * (1.0 / pow((double)distance, 2)) * (dx / distance);
                _fy = -Kobs * multiplicador_repulsao * (1.0 / distance - 1.0 / (influence * 2)) * (1.0 / pow((double)distance, 2)) * (dy / distance);
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

#ifdef mudancas
    if (estado == ENTRANDO)
    {
        if (min_distance < SECURITY_DIST_ENTRANDO)
        {
            multiplicador_repulsao += 0.1;
        }
        else
        {
            qtd_sem_aumentar_repulsao += 1;
        }
        if (qtd_sem_aumentar_repulsao > 4 && multiplicador_repulsao > 1)
        {
            multiplicador_repulsao -= 0.01;
        }
    }
    if (estado == SAINDO)
    {
        if (min_distance < SECURITY_DIST_SAINDO)
        {
            multiplicador_repulsao += 0.1;
        }
        else if (multiplicador_repulsao > 1)
        {
            multiplicador_repulsao -= 0.05;
        }
    }
#endif
#ifdef DEBUG_FORCES
    fv.setRepulsiveForces(fx_, fy_);
#endif
}

void PCCEEV2::calculeAttractiveForce(double &fx, double &fy, double &norm)
{
#ifdef mudancas
    if (estado == ENTRANDO)
    {
        fx = Ka * (fx) / norm;
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
}

Vec2 PCCEEV2::rotacionarForca(const Vec2 &forca, double angulo_rad)
{
    double cos_a = std::cos(angulo_rad);
    double sin_a = std::sin(angulo_rad);

    return {
        forca.x * cos_a - forca.y * sin_a,
        forca.x * sin_a + forca.y * cos_a};
}

void PCCEEV2::calculateNormalForce(double &fx, double &fy, double &norm)
{
    bool horario = true;
    Vec2 p1 = {100, 100};
    Vec2 p2 = {-999999, 100};
    Vec2 forca_local;

    double dx = p2.x - p1.x;
    double dy = p2.y - p1.y;

    // 2. Vetor normal à reta (90°)
    double nx = horario ? dy : -dy;
    double ny = horario ? -dx : dx;
    // 3. Normaliza
    double len = std::sqrt(nx * nx + ny * ny);
    if (len == 0)
        forca_local = {0, 0};

    nx /= len;
    ny /= len;
    cout << "Normal unitária: " << nx << " - " << ny << endl;

    // 4. Aplica magnitude proporcional à distância
    nx *= norm;
    ny *= norm;

    // 5. Transforma a força para o referencial local do robô
    Pose pose = pos->GetPose();
    double cos_r = std::cos(-pose.a); // rotação inversa para referencial do robô
    double sin_r = std::sin(-pose.a);

    forca_local.x = nx * cos_r - ny * sin_r;
    forca_local.y = nx * sin_r + ny * cos_r;
    cout << "Normal unitária: (" << forca_local.x << ", " << forca_local.y << ")" << m_x - 100 << "," << m_y - 100 << " - " << m_th << endl;
#ifdef SHOW_NORMAL_OUTPUT_FORCE
    fv.setNormalOutputForce(forca_local.x, forca_local.y);
#endif
}
// Implements the main loop of robot.
// Also contain robot controller and
// probabilistic finite state machine codes

void PCCEEV2::walk()
{
    double fx = 0;
    double fy = 0;

    double angTarget;
    double linAccel;
    double rotAccel;

    numIterations++;

    // how many times robot stall?
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
        multiplicador_repulsao = 1;
        pos->SetColor(GOING_OUT_COLOR);

        numIterationsReachGoal = numIterations;
        numIterations = 0;
    }
    if (finished && (distance(m_x, m_y, waypoints[0][0], waypoints[0][1]) >= distant_radius_to_finish))
    {
        // connection.finish(m_id, numIterationsReachGoal, numIterations, stalls, theWorld->SimTimeNow());
        FinalLog::refresh(numIterationsReachGoal, numIterations, 0, stalls, theWorld->SimTimeNow());
        FinalLog::finish();
        pos->SetColor(Color(0, 0, 0));
        finish();
        finished = false;
    }

#ifdef CHECK_DEAD_ROBOTS
    if (numIterations > DEAD_ITERATIONS)
    {
        // connection.finish(m_id, numIterations, 0, stalls, theWorld->SimTimeNow());
        FinalLog::refresh(numIterationsReachGoal, numIterations, 0, stalls, theWorld->SimTimeNow());
        FinalLog::finish();
        pos->SetColor(Color(0, 0, 0));
        finish();
    }
#endif
    double norm = 0;
    destineX = waypoints[currentWaypoint][0];
    destineY = waypoints[currentWaypoint][1];

    fx = (destineX - m_x);
    fy = (destineY - m_y);
    norm = sqrt(pow(fx, 2) + pow(fy, 2));
    calculeAttractiveForce(fx, fy, norm);
#ifdef normalForce
    calculateNormalForce(fx, fy, norm);
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

// returns the distance between a robot and your goal
double PCCEEV2::pho()
{
    return hypot(m_x - destineX, m_y - destineY);
}

// Initializes values for sensing with laser, depending on the world file used.
void PCCEEV2::init_laser()
{
    // init laser configuration for use in getBearing()
    ModelRanger::Sensor sensor = laser->GetSensors()[0];
    LASER_FOV = rtod(sensor.fov);
    LASER_SAMPLES = sensor.sample_count;
    laser->vis.showArea.set(0);
}

// Used for get the angle of some laser beam on respect to the orientation of robot
inline double PCCEEV2::getBearing(int i)
{
    return dtor(-LASER_FOV / 2 + (LASER_FOV / (LASER_SAMPLES - 1)) * i);
}

// Initialize robot position data, i.e. angular and linear velocities,
// initial waypoint to search and seed to random number generator
void PCCEEV2::init_position_data()
{
    currentWaypoint = 0;
    linSpeed = 0;
    rotSpeed = 0;
    srand(m_id * time(NULL));
}

// Convert a integer to string
string PCCEEV2::intToStr(int integer)
{
    ostringstream stringNumero;

    stringNumero << integer;

    return stringNumero.str();
}

// Saturate  a vector to a limit modulo, keeping scale.
void PCCEEV2::saturation(double &x, double &y, double limit)
{
    double factor;

    // Saturation (keeping scale between x and y)
    if ((x > limit) || (y > limit))
    {
        if (x > y)
        {
            factor = x / limit;
            x = x / factor;
            y = y / factor;
        }
        else
        {
            factor = y / limit;
            y = y / factor;
            x = x / factor;
        }
    }
    if ((x < -limit) || (y < -limit))
    {
        if (x < y)
        {
            factor = x / -limit;
            x = x / factor;
            y = y / factor;
        }
        else
        {
            factor = y / -limit;
            y = y / factor;
            x = x / factor;
        }
    }
}

// Substract two angle values (in radians). The result value lies between
//-2 PI and 2 PI.
double PCCEEV2::angDiff(double end, double begin)
{
    double returnMe = end - begin;

    if (returnMe > PI)
        returnMe = -(2 * PI - returnMe);
    else if (returnMe < -PI)
        returnMe = 2 * PI + returnMe;

    return returnMe;
}