import Map "mo:core/Map";
import List "mo:core/List";
import Time "mo:core/Time";
import Int "mo:core/Int";
import Text "mo:core/Text";
import Iter "mo:core/Iter";
import Char "mo:core/Char";
import Order "mo:core/Order";
import Array "mo:core/Array";
import Runtime "mo:core/Runtime";
import Principal "mo:core/Principal";

actor {
  module Insight {
    public func compare(insight1 : Insight, insight2 : Insight) : Order.Order {
      switch (Int.compare(insight1.timestamp, insight2.timestamp)) {
        case (#equal) { Text.compare(insight1.content, insight2.content) };
        case (order) { order };
      };
    };
  };

  type ProjectId = Nat;

  type Scale = {
    #indie;
    #studio;
    #blockbuster;
  };

  type BudgetLevel = {
    #low;
    #medium;
    #high;
  };

  type TalentStrategy = {
    #unknown;
    #emerging;
    #established;
    #starDriven;
  };

  type ProductionHealth = {
    #good;
    #atRisk;
    #critical;
  };

  type AudienceType = {
    #niche;
    #broad;
    #mainstream;
  };

  type MarketingBudgetLevel = {
    #low;
    #medium;
    #high;
    #unassigned;
  };

  type PrimaryMarketingChannel = {
    #influencer;
    #festival;
    #digitalAds;
    #pr;
    #undefined;
  };

  type ReleaseModel = {
    #theatre;
    #ott;
    #hybrid;
  };

  type DistributionConfidence = {
    #low;
    #medium;
    #high;
  };

  type CompetitionLevel = {
    #low;
    #medium;
    #high;
  };

  type DiscoverabilityRisk = {
    #low;
    #medium;
    #high;
  };

  type AudienceResponse = {
    #weak_;
    #moderate_;
    #strong;
  };

  type FilmProject = {
    id : ProjectId;
    title : Text;
    currentPhase : Nat;
    genre : Text;
    language : Text;
    theme : Text;
    scale : Scale;
    budgetLevel : BudgetLevel;
    talentStrategy : TalentStrategy;
    plannedShootDays : Int;
    actualShootDays : ?Int;
    productionHealth : ProductionHealth;
    audienceType : AudienceType;
    marketingBudgetLevel : MarketingBudgetLevel;
    primaryMarketingChannel : PrimaryMarketingChannel;
    releaseModel : ReleaseModel;
    distributionConfidence : DistributionConfidence;
    lastUpdated : Int;
  };

  public type Insight = {
    content : Text;
    timestamp : Int;
  };

  var nextProjectId : ProjectId = 1;

  let filmProjects = Map.empty<ProjectId, FilmProject>();
  let projectInsights = Map.empty<ProjectId, List.List<Insight>>();

  var hasRuntimeTrapped = false;

  public shared ({ caller }) func createFilmProject(
    title : Text,
    genre : Text,
    language : Text,
    theme : Text,
    scale : Scale,
    budgetLevel : BudgetLevel,
    talentStrategy : TalentStrategy,
    plannedShootDays : Int,
    audienceType : AudienceType,
    marketingBudgetLevel : MarketingBudgetLevel,
    primaryMarketingChannel : PrimaryMarketingChannel,
    releaseModel : ReleaseModel,
    distributionConfidence : DistributionConfidence,
  ) : async ProjectId {
    if (title.size() > 100) {
      Runtime.trap("Title must be 100 characters or less");
      hasRuntimeTrapped := true;
    };

    let projectId = nextProjectId;
    nextProjectId += 1;

    let newProject : FilmProject = {
      id = projectId;
      title;
      currentPhase = 1;
      genre;
      language;
      theme;
      scale;
      budgetLevel;
      talentStrategy;
      plannedShootDays;
      actualShootDays = null;
      productionHealth = #good;
      audienceType;
      marketingBudgetLevel;
      primaryMarketingChannel;
      releaseModel;
      distributionConfidence;
      lastUpdated = Time.now();
    };

    filmProjects.add(projectId, newProject);
    let emptyInsights = List.empty<Insight>();
    projectInsights.add(projectId, emptyInsights);

    projectId;
  };

  public query ({ caller }) func getFilmProject(projectId : ProjectId) : async ?FilmProject {
    filmProjects.get(projectId);
  };

  public query ({ caller }) func getAllFilmProjects() : async [FilmProject] {
    filmProjects.values().toArray();
  };

  public shared ({ caller }) func updateFilmProjectPhase(
    projectId : ProjectId,
    newPhase : Nat,
  ) : async () {
    switch (filmProjects.get(projectId)) {
      case (null) {
        Runtime.trap("Film project not found");
        hasRuntimeTrapped := true;
      };
      case (?project) {
        if (newPhase < 1 or newPhase > 8) {
          Runtime.trap("Phase must be between 1 and 8");
          hasRuntimeTrapped := true;
        };

        let updatedProject = {
          id = project.id;
          title = project.title;
          currentPhase = newPhase;
          genre = project.genre;
          language = project.language;
          theme = project.theme;
          scale = project.scale;
          budgetLevel = project.budgetLevel;
          talentStrategy = project.talentStrategy;
          plannedShootDays = project.plannedShootDays;
          actualShootDays = project.actualShootDays;
          productionHealth = project.productionHealth;
          audienceType = project.audienceType;
          marketingBudgetLevel = project.marketingBudgetLevel;
          primaryMarketingChannel = project.primaryMarketingChannel;
          releaseModel = project.releaseModel;
          distributionConfidence = project.distributionConfidence;
          lastUpdated = Time.now();
        };

        filmProjects.add(projectId, updatedProject);
      };
    };
  };

  public shared ({ caller }) func addProjectInsight(
    projectId : ProjectId,
    content : Text,
  ) : async () {
    switch (filmProjects.get(projectId)) {
      case (null) {
        Runtime.trap("Film project not found");
        hasRuntimeTrapped := true;
      };
      case (?_) {
        let newInsight : Insight = {
          content;
          timestamp = Time.now();
        };

        switch (projectInsights.get(projectId)) {
          case (null) {
            let insights = List.empty<Insight>();
            insights.add(newInsight);
            projectInsights.add(projectId, insights);
          };
          case (?insights) {
            insights.add(newInsight);
          };
        };
      };
    };
  };

  public query ({ caller }) func getProjectInsights(projectId : ProjectId) : async [Insight] {
    switch (projectInsights.get(projectId)) {
      case (null) { [] };
      case (?insights) {
        insights.toArray().sort();
      };
    };
  };

  public shared ({ caller }) func updateFilmProject(
    projectId : ProjectId,
    title : Text,
    phase : Int,
    genre : Text,
    language : Text,
    theme : Text,
    scale : Scale,
    budgetLevel : BudgetLevel,
    talentStrategy : TalentStrategy,
    plannedShootDays : Int,
    actualShootDays : Int,
    productionHealth : ProductionHealth,
    audienceType : AudienceType,
    marketingBudgetLevel : MarketingBudgetLevel,
    primaryMarketingChannel : PrimaryMarketingChannel,
    releaseModel : ReleaseModel,
    distributionConfidence : DistributionConfidence,
  ) : async () {
    switch (filmProjects.get(projectId)) {
      case (null) {
        Runtime.trap("Film project not found");
        hasRuntimeTrapped := true;
      };
      case (?_) {
        let updatedProject : FilmProject = {
          id = projectId;
          title;
          // CERES: PHASE TYPE CONVERSION
          currentPhase = phase.toNat();
          genre;
          language;
          theme;
          scale;
          budgetLevel;
          talentStrategy;
          plannedShootDays;
          actualShootDays = ?actualShootDays;
          productionHealth;
          audienceType;
          marketingBudgetLevel;
          primaryMarketingChannel;
          releaseModel;
          distributionConfidence;
          lastUpdated = Time.now();
        };

        filmProjects.add(projectId, updatedProject);
      };
    };
  };

  public query ({ caller }) func getFilmProjectWithInsights(projectId : ProjectId) : async (FilmProject, [Insight]) {
    switch (filmProjects.get(projectId)) {
      case (null) {
        Runtime.trap("Film project not found");
      };
      case (?project) {
        let sortedInsights = switch (projectInsights.get(projectId)) {
          case (null) { [] };
          case (?insights) {
            insights.toArray().sort();
          };
        };
        (project, sortedInsights);
      };
    };
  };

  public query ({ caller }) func getMaxProjectId() : async Nat {
    if (nextProjectId > 1) { nextProjectId - 1 } else { 0 };
  };

  public query ({ caller }) func didRuntimeTrap() : async Bool {
    hasRuntimeTrapped;
  };

  public query ({ caller }) func getProjectTitlesStartingWith(letter : Text) : async [Text] {
    let filteredTitles = filmProjects.values().toArray().values().filter(
      func(project) {
        let title = project.title;
        title.size() > 0 and Text.fromIter([title.chars().next().unwrap()].values()) == letter
      }
    );
    filteredTitles.map(func(project) { project.title }).toArray();
  };
};
