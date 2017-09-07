#include "connectionlocal.h"

//Given a message, compute the distance between the sender and the receiver
double ConnectionLocal::dist(double m_x, double m_y, double *msg)
{
   return hypot(m_x - msg[MSG_POS_MY_X],m_y - msg[MSG_POS_MY_Y]);
}

//Receive a msg. With received correctly, returns true
bool ConnectionLocal::receiveMsg(double m_x, double m_y, unsigned int m_id, double *msg, int size_msg){
  MessageContainer::iterator it;
  for ( it=(*pool)[pool_id].begin() ; it != (*pool)[pool_id].end(); it++ ){
    if (dist(m_x,m_y,(*it).msg) < commArea && m_id != (unsigned int) (*it).msg[MSG_POS_MY_ID]){
      unsigned int i;
      for (i = 0; i < size_msg;i++) msg[i] = (*it).msg[i];
      (*pool)[pool_id].clear();
      return true;
    }
  }
  return false;
}

//send a msg
void ConnectionLocal::sendMsg(double *msg, int size_msg){
  Pool_t::iterator it;
  for ( it=pool->begin() ; it != pool->end(); it++ ){
    (*it).push_front(Message(msg,size_msg));
  }
  numMessages++;
}

//initialize the informations for connection
void ConnectionLocal::init_connection(string path){
  numMessages = 0;
  pool_id = pool->size();
  MessageContainer s;
  pool->push_back(s); 
  FinalLog::init(path);
}

void ConnectionLocal::init_connection(double prob){
  numMessages = 0;
  pool_id = pool->size();
  MessageContainer s;
  pool->push_back(s); 
  FinalLog::init(prob);
}

ConnectionLocal::ConnectionLocal(Pool_t* apool){
  pool = apool;
}

//informs the logger that the robot using this class end your task, refreshing statistics 
void ConnectionLocal::finish(int m_id, int numIterationsEnter, int numIterationsExit, int stalls){
  FinalLog::refresh(numIterationsEnter, numIterationsExit, numMessages, stalls);
  FinalLog::finish();
}


