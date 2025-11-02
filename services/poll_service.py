import json
from typing import Dict, Optional
from sqlalchemy.orm import Session
from database import Poll, Voter
from config import settings


class PollService:
    @staticmethod
    def create_poll(db: Session, question: str, candidates: Dict[str, str]) -> Poll:
        """Create a new poll"""
        poll = Poll(
            question=question,
            candidates=json.dumps(candidates, ensure_ascii=False),
            votes=json.dumps({}),
            channel_id=settings.CHANNEL_ID
        )
        db.add(poll)
        db.commit()
        db.refresh(poll)
        return poll
    
    @staticmethod
    def get_poll(db: Session, message_id: int) -> Optional[Poll]:
        """Get poll by message_id"""
        return db.query(Poll).filter(Poll.message_id == message_id).first()
    
    @staticmethod
    def update_message_id(db: Session, poll_id: int, message_id: int):
        """Update poll's message_id after sending to channel"""
        poll = db.query(Poll).filter(Poll.id == poll_id).first()
        if poll:
            poll.message_id = message_id
            db.commit()
    
    @staticmethod
    def has_user_voted(db: Session, user_id: int, poll_message_id: int) -> bool:
        """Check if user has already voted"""
        voter = db.query(Voter).filter(
            Voter.user_id == user_id,
            Voter.poll_message_id == poll_message_id
        ).first()
        return voter is not None and voter.has_voted
    
    @staticmethod
    def vote(db: Session, user_id: int, poll_message_id: int, candidate_id: str) -> bool:
        """Record a vote. Returns True if successful, False if user already voted"""
        if PollService.has_user_voted(db, user_id, poll_message_id):
            return False
        
        poll = PollService.get_poll(db, poll_message_id)
        if not poll:
            return False
        
        votes = json.loads(poll.votes)
        votes[str(user_id)] = candidate_id
        poll.votes = json.dumps(votes, ensure_ascii=False)
        
        # Mark user as voted
        voter = db.query(Voter).filter(
            Voter.user_id == user_id,
            Voter.poll_message_id == poll_message_id
        ).first()
        
        if not voter:
            voter = Voter(user_id=user_id, poll_message_id=poll_message_id, has_voted=True)
            db.add(voter)
        else:
            voter.has_voted = True
        
        db.commit()
        return True
    
    @staticmethod
    def get_vote_counts(db: Session, poll_message_id: int) -> Dict[str, int]:
        """Get vote counts for each candidate"""
        poll = PollService.get_poll(db, poll_message_id)
        if not poll:
            return {}
        
        votes = json.loads(poll.votes)
        candidates = json.loads(poll.candidates)
        counts = {cid: 0 for cid in candidates.keys()}
        
        for user_vote in votes.values():
            if user_vote in counts:
                counts[user_vote] += 1
        
        return counts
    
    @staticmethod
    def get_poll_data(db: Session, poll_message_id: int) -> Optional[Dict]:
        """Get complete poll data"""
        poll = PollService.get_poll(db, poll_message_id)
        if not poll:
            return None
        
        return {
            "question": poll.question,
            "candidates": json.loads(poll.candidates),
            "vote_counts": PollService.get_vote_counts(db, poll_message_id)
        }

