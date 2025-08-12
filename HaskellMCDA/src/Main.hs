{-# LANGUAGE DataKinds #-}
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TypeOperators #-}

module Main where

import Prelude hiding (id)
import GHC.Generics (Generic)
import Data.Aeson (FromJSON, ToJSON)
import qualified Data.Aeson as Aeson
import qualified Data.Map.Strict as M
import Data.Map.Strict (Map)
import Data.Text (Text)
import qualified Data.Text as T
import Data.List (sortBy)
import Network.Wai (Application)
import Network.Wai.Handler.Warp (run)
import Servant

-- Request/Response types

data Candidate = Candidate
  { id :: Int
  , features :: Map Text Double
  } deriving (Show, Generic)

instance FromJSON Candidate
instance ToJSON Candidate

data RankRequest = RankRequest
  { candidates :: [Candidate]
  , weights :: Map Text Double
  , method :: Text
  } deriving (Show, Generic)

instance FromJSON RankRequest
instance ToJSON RankRequest

data Ranked = Ranked
  { rid :: Int
  , score :: Double
  } deriving (Show, Generic)

instance ToJSON Ranked where
  toJSON (Ranked i s) = Aeson.object ["id" Aeson..= i, "score" Aeson..= s]

data RankResponse = RankResponse
  { rankedCandidates :: [Ranked]
  , explanation :: Text
  } deriving (Show, Generic)

instance ToJSON RankResponse

type API = "rank" :> ReqBody '[JSON] RankRequest :> Post '[JSON] RankResponse

server :: Server API
server = rankHandler

rankHandler :: RankRequest -> Handler RankResponse
rankHandler req = do
  let ws = normalizeWeights (weights req)
      featsList = fmap features (candidates req)
      names = collectAllKeys featsList
      -- Build decision matrix aligning features across candidates, fill missing with 0
      matrix = fmap (\fs -> map (\k -> M.findWithDefault 0 k fs) names) featsList
      wvec = map (\k -> M.findWithDefault 0 k ws) names
      scores = topsis wvec matrix
      ranked = zipWith Ranked (map id (candidates req)) scores
      rankedSorted = reverse $ sortByScore ranked
      expl = "Ranked using TOPSIS with weights: " <> prettyWeights ws
  pure $ RankResponse rankedSorted expl

normalizeWeights :: Map Text Double -> Map Text Double
normalizeWeights m =
  let s = sum (M.elems m)
  in if s <= 0 then m else M.map (/ s) m

collectAllKeys :: [Map Text Double] -> [Text]
collectAllKeys = M.keys . M.unions

-- Simple TOPSIS implementation
-- matrix: [candidate][criterion]
-- weights: [criterion]
topsis :: [Double] -> [[Double]] -> [Double]
topsis weights matrix =
  let cols = transpose matrix
      -- Normalize columns
      normCol col =
        let denom = sqrt (sum (map (\x -> x * x) col))
        in if denom == 0 then replicate (length col) 0 else map (/ denom) col
      norm = map normCol cols
      -- Weighted normalized
      wnorm = zipWith (\w col -> map (* w) col) weights norm
      -- Ideal best/worst
      idealBest = map maximum wnorm
      idealWorst = map minimum wnorm
      -- Distances for each candidate
      distancesTo v = map (\row -> sqrt $ sum $ zipWith (\a b -> (a - b) ^ (2 :: Int)) row v) (transpose wnorm)
      dPlus  = distancesTo idealBest
      dMinus = distancesTo idealWorst
      -- Relative closeness
      score i = let dp = dPlus !! i; dm = dMinus !! i in if dp + dm == 0 then 0 else dm / (dp + dm)
  in map score [0 .. length matrix - 1]

sortByScore :: [Ranked] -> [Ranked]
sortByScore = sortBy (\a b -> compare (score a) (score b))

prettyWeights :: Map Text Double -> Text
prettyWeights m = T.intercalate ", " [k <> ":" <> tshow v | (k,v) <- M.toList m]

tshow :: Show a => a -> Text
tshow = T.pack . show

api :: Proxy API
api = Proxy

app :: Application
app = serve api server

main :: IO ()
main = run 8081 app

-- Local transpose to avoid extra imports
transpose :: [[a]] -> [[a]]
transpose [] = []
transpose ([]:_) = []
transpose x = map head x : transpose (map tail x)

